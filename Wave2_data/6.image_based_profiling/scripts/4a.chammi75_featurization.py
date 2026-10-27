#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import os
import pathlib
import sys

import natsort
import numpy as np
import pandas as pd
import tifffile
import torch
from timelapse_utils.featurization_utils.chammi75_featurization import (
    call_chammi75_featurization_pipeline,
    get_chammi75_model,
)
from timelapse_utils.featurization_utils.feature_writing_utils import (
    format_morphology_feature_name,
)
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)
from timelapse_utils.image_utils.timelapse_image_utils import (
    crop_from_centroid,
    extract_x_y_centroid_from_image_based_profile,
)

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)

if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm


# In[2]:


def featurize_well_fov_timepoint_label(
    well_fov_timepoint: str,
    label: int,
    image: np.ndarray,
    image_channel_name: str,
    model: torch.nn.Module,
    x_y_centroid: tuple,
) -> pd.DataFrame:
    """
    Featurize a single label (cell) at a given well_fov_timepoint using the CHAMMI75 model.

    Args:
        df_of_label_profiles (pd.DataFrame): DataFrame containing the profiles of all labels at the given well_fov_timepoint.
        label_id (int): The unique identifier for the label to featurize.

    Returns:
        pd.DataFrame: A DataFrame containing the extracted features for the specified label.
    """

    well, fov, timepoint = well_fov_timepoint.split("_")
    list_of_feature_dicts = []

    bbox = crop_from_centroid(
        center_x=x_y_centroid[0],
        center_y=x_y_centroid[1],
        image_shape=image.shape,
        radius=30,
    )

    cropped_image = image[bbox[0] : bbox[2], bbox[1] : bbox[3]]

    chammi75_features = call_chammi75_featurization_pipeline(
        cropped_image=cropped_image, model=chammi75_model
    )
    # make a new dictionary to hold all features
    combined_feature_dict = {
        "feature_name": [],
        "feature_value": [],
        "Metadata_Nuclei_Number_Object_Number": [],
        "Metadata_Well_FOV": [],
        "Metadata_Time": [],
        "Metadata_Cells_AreaShape_Center_X": [],
        "Metadata_Cells_AreaShape_Center_Y": [],
    }

    for i, feat_value in enumerate(chammi75_features[0]):
        combined_feature_dict["feature_name"].append(
            format_morphology_feature_name(
                compartment="Nucleocentric",
                channel=image_channel_name,
                feature_type="MorphEM",
                measurement=f"Feature{i}",
            )
        )
        combined_feature_dict["feature_value"].append(feat_value.item())
        combined_feature_dict["Metadata_Nuclei_Number_Object_Number"].append(label)
        combined_feature_dict["Metadata_Well_FOV"].append(f"{well}_{fov}")
        combined_feature_dict["Metadata_Time"].append(timepoint)
        combined_feature_dict["Metadata_Cells_AreaShape_Center_X"].append(
            x_y_centroid[0]
        )
        combined_feature_dict["Metadata_Cells_AreaShape_Center_Y"].append(
            x_y_centroid[1]
        )
    df = pd.DataFrame(combined_feature_dict)

    return df


# In[3]:


if not in_notebook:
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--well_fov",
        type=str,
        help="The well, fov, and timepoint to featurize in the format 'well_fov_timepoint', e.g. 'A1_1_1'",
    )
    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    well_fov = args.well_fov
    plate_name = args.plate_name
else:
    plate_name = "plate_2"
    well_fov = "B2_2"


well, fov = well_fov.split("_")
well_fov = f"{well}_{fov}"


image_base_dir = bandicoot_check(
    root_dir=root_dir,
    bandicoot_mount_path=pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(),
)

profile_file_path = pathlib.Path(
    image_base_dir
    / "processed_data"
    / "8.annotated_profiles"
    / plate_name
    / f"{well_fov}_annotated.parquet"
).resolve(strict=True)

channel_image_dir = pathlib.Path(
    image_base_dir / "processed_data" / "0.renamed_files" / plate_name / well_fov
).resolve(strict=True)

feature_extracted_file = pathlib.Path(
    image_base_dir
    / "processed_data"
    / "9a.morphem_extracted_features"
    / plate_name
    / f"{well_fov}_morphem_features.parquet"
).resolve()
feature_extracted_file.parent.mkdir(exist_ok=True, parents=True)

if feature_extracted_file.exists():
    # exit the script/notebook we already have these features extracted
    sys.exit(
        f"Features already extracted for {well_fov} at {feature_extracted_file}. Exiting."
    )


# In[4]:


channel_mapping = {
    "C1": "ChomaLIVE561",
    "C2": "ChomaLIVE488",
    "C3": "SYTOXGreen",
    "C4": "NucleoLIVE",
}


# In[5]:


# get a list of each channel to featurize
channel_paths = natsort.natsorted(list(channel_image_dir.glob(f"{well_fov}_*_C*.tiff")))
# add each timepoint, and channel to the channel_images dictionary
dict_of_images = {
    "timepoint": [],
    "well_fov": [],
    "well_fov_time": [],
    "image_path": [],
    "channel": [],
}
for path in channel_paths:
    timepoint = path.stem.split("_")[-2]
    channel = channel_mapping[path.stem.split("_")[-1]]
    dict_of_images["timepoint"].append(timepoint)
    dict_of_images["well_fov"].append(well_fov)
    dict_of_images["well_fov_time"].append(f"{well_fov}_{timepoint}")
    dict_of_images["image_path"].append(path)
    dict_of_images["channel"].append(channel)
df_of_images = pd.DataFrame(dict_of_images)
# pivot wide so each channel is a column, and the values are the image paths
df_of_images = df_of_images.pivot(
    index=["well_fov_time", "well_fov", "timepoint"],
    columns="channel",
    values="image_path",
).reset_index()
df_of_images.columns.name = None
df_of_images.sort_values(
    by="well_fov_time",  # replace with whichever column you actually want to sort on
    key=lambda x: x.map(natsort.natsort_keygen()),
    inplace=True,
)
df_of_images["well_fov_time"] = df_of_images["well_fov_time"].str.replace("T", "")


# In[6]:


device = "cuda" if torch.cuda.is_available() else "cpu"
chammi75_model = get_chammi75_model(device)


# In[7]:


# set columns names to parse
# read in the annotated profiles parquet file, but only the columns we need to extract features
columns_to_read_in = [
    "Metadata_Well_FOV_Time",
    "Metadata_Cells_AreaShape_Center_X",
    "Metadata_Cells_AreaShape_Center_Y",
    "Metadata_Nuclei_Number_Object_Number",
    "Metadata_Cells_Number_Object_Number",
]
channel_path_column_names = ["ChomaLIVE488", "ChomaLIVE561", "NucleoLIVE", "SYTOXGreen"]
annotated_df = pd.read_parquet(profile_file_path, columns=columns_to_read_in)


# In[8]:


list_of_dfs_to_merge = []
for row in tqdm.tqdm(
    df_of_images.itertuples(),
    total=len(df_of_images),
    desc=f"Featurizing {well_fov} with CHAMMI75",
    leave=True,
):
    well_fov_time = row.well_fov_time
    well_fov_time_out_file_path = pathlib.Path(
        f"{image_base_dir}/processed_data/9a.morphem_extracted_features/{plate_name}/{well_fov_time}_morphem_features.parquet"
    ).resolve()
    well_fov_time_out_file_path.parent.mkdir(exist_ok=True, parents=True)
    if well_fov_time_out_file_path.exists():
        print(
            f"Features already extracted for {well_fov_time} at {well_fov_time_out_file_path}. Skipping."
        )
        continue
    all_channels_list_dfs = []
    for channel in tqdm.tqdm(
        channel_path_column_names,
        desc="Processing channels",
        total=len(channel_path_column_names),
        leave=False,
    ):

        image_path = getattr(row, channel)
        image_channel_name = channel
        image = tifffile.imread(image_path)
        df_of_label_profiles = annotated_df[
            annotated_df["Metadata_Well_FOV_Time"] == well_fov_time
        ]
        list_of_dfs_to_concat = []

        for label in tqdm.tqdm(
            df_of_label_profiles["Metadata_Nuclei_Number_Object_Number"].unique(),
            desc="Processing labels",
            total=len(
                df_of_label_profiles["Metadata_Nuclei_Number_Object_Number"].unique()
            ),
            leave=False,
        ):
            tmp_df = df_of_label_profiles[
                df_of_label_profiles["Metadata_Nuclei_Number_Object_Number"] == label
            ]
            x_y_centroid = extract_x_y_centroid_from_image_based_profile(tmp_df, label)
            feature_df = featurize_well_fov_timepoint_label(
                well_fov_timepoint=well_fov_time,
                label=label,
                image=image,
                image_channel_name=image_channel_name,
                model=chammi75_model,
                x_y_centroid=x_y_centroid,
            )
            list_of_dfs_to_concat.append(feature_df)
        list_of_dfs_to_merge.append(
            pd.concat(list_of_dfs_to_concat, axis=0, ignore_index=True)
        )
    well_fov_time_df = pd.DataFrame()
    for df in list_of_dfs_to_merge:
        if well_fov_time_df.empty:
            well_fov_time_df = df
        else:
            well_fov_time_df = pd.merge(
                well_fov_time_df,
                df,
                on=well_fov_time_df.columns.intersection(df.columns).tolist(),
                how="inner",
            )

    well_fov_time_df.to_parquet(well_fov_time_out_file_path)


# In[9]:


# concat the timepoint dataframes into a single dataframe for the well_fov
parent_path = pathlib.Path(
    f"{image_base_dir}/processed_data/9a.morphem_extracted_features/{plate_name}/"
).resolve()
list_of_well_fov_timepoint_files = list(
    parent_path.glob(f"{well_fov}_*_morphem_features.parquet")
)
list_of_well_fov_timepoint_files
final_well_fov_df = pd.concat(
    [pd.read_parquet(file) for file in list_of_well_fov_timepoint_files],
    axis=0,
    ignore_index=True,
)
output_file_path = pathlib.Path(
    f"{image_base_dir}/processed_data/9b.combined_morphem_extracted_features/{plate_name}/{well_fov}_morphem_features.parquet"
)
output_file_path.parent.mkdir(exist_ok=True, parents=True)
final_well_fov_df.to_parquet(output_file_path)
