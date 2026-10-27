#!/usr/bin/env python
# coding: utf-8

# # Normalize annotated single cells using negative control

# ## Import libraries

# In[1]:


import argparse
import os
import pathlib

import natsort
import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import infer_cp_features, output
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


# ## Set paths and variables

# In[2]:


if in_notebook:
    import tqdm.notebook as tqdm

    plate_name = "plate_2"
else:
    import tqdm

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    plate_name = args.plate_name


# In[3]:


# load in platemap file as a pandas dataframe
image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
sc_tracks_path = pathlib.Path(
    f"{image_base_dir}/9.single_Cell_tracks_merged/{plate_name}/"
).resolve(strict=True)

plate_map_file_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/plate_2/platemap.csv"
).resolve(strict=True)
train_test_split_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/train_test_split_indices/{plate_name}/"
).resolve()
normalized_profiles_path = pathlib.Path(
    f"{image_base_dir}/10.normalized_profiles/{plate_name}/"
).resolve()
normalized_profiles_path.mkdir(exist_ok=True, parents=True)

normalization_params_file_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/notebooks/normalized_df.onnx"
).resolve()
# unlink to generate new each time
if normalization_params_file_path.exists():
    normalization_params_file_path.unlink()


# In[4]:


plate_map_df = pd.read_csv(plate_map_file_path)
control_well_fovs = plate_map_df.loc[
    (plate_map_df["Metadata_Inducer1"] == "DMSO")
    & (plate_map_df["Metadata_Inducer2"] == "DMSO")
    & (plate_map_df["Metadata_Inhibitor"] == "DMSO")
]["Metadata_Well"].unique()
control_well_fovs = [x.replace("0", "") for x in control_well_fovs]
print(f"Found {len(control_well_fovs)} control wells in the platemap file.")
print(f"Control wells: {control_well_fovs}")


# In[5]:


well_fov_profile_and_split_dict = {
    "well_fov": [],
    "profile_path": [],
    "train_test_split_path": [],
    "norm_output_path": [],
}


# In[6]:


# load each of the control_well_fovs train test split indices as a pandas dataframe
train_test_split_path_list = natsort.natsorted(
    list(train_test_split_path.glob("*.parquet")), key=lambda x: x.name
)


# In[7]:


# load in the the control well_fovs as a pandas dataframe
sc_tracks_path_list = list(sc_tracks_path.glob("*.parquet"))
sc_tracks_path_list = natsort.natsorted(sc_tracks_path_list, key=lambda x: x.stem)
for sc_tracks_path in tqdm.tqdm(sc_tracks_path_list):
    well_fov = sc_tracks_path.stem.replace("_sc_tracks_merged", "")

    # check if well_fov is in the well_fov_profile_and_split_dict
    if (
        well_fov not in well_fov_profile_and_split_dict["well_fov"]
        and sc_tracks_path not in well_fov_profile_and_split_dict["profile_path"]
    ):
        well_fov_profile_and_split_dict["well_fov"].append(well_fov)
        well_fov_profile_and_split_dict["profile_path"].append(sc_tracks_path)
    elif (
        well_fov in well_fov_profile_and_split_dict["well_fov"]
        and sc_tracks_path not in well_fov_profile_and_split_dict["profile_path"]
    ):
        # find the index of the well_fov in the well_fov_profile_and_split_dict
        index = well_fov_profile_and_split_dict["well_fov"].index(well_fov)
        well_fov_profile_and_split_dict["profile_path"][index] = sc_tracks_path
    output_path = pathlib.Path(
        f"{normalized_profiles_path}/{well_fov}_normalized.parquet"
    )
    well_fov_profile_and_split_dict["norm_output_path"].append(output_path)
    well_fov_profile_and_split_dict["train_test_split_path"].append(None)

# load in the the control well_fovs as a pandas dataframe

for sc_split in tqdm.tqdm(train_test_split_path_list):
    well_fov = sc_split.stem.strip("_train_test_split")

    # check if well_fov is in the well_fov_profile_and_split_dict
    if (
        well_fov not in well_fov_profile_and_split_dict["well_fov"]
        and sc_split not in well_fov_profile_and_split_dict["train_test_split_path"]
    ):
        well_fov_profile_and_split_dict["well_fov"].append(well_fov)
        well_fov_profile_and_split_dict["train_test_split_path"].append(sc_split)
    elif (
        well_fov in well_fov_profile_and_split_dict["well_fov"]
        and sc_split not in well_fov_profile_and_split_dict["train_test_split_path"]
    ):
        # find the index of the well_fov in the well_fov_profile_and_split_dict
        index = well_fov_profile_and_split_dict["well_fov"].index(well_fov)
        well_fov_profile_and_split_dict["train_test_split_path"][index] = sc_split


# In[8]:


# Set the samples needed for fit
samples = (
    "Metadata_Inducer1 == 'DMSO' "
    "& Metadata_Inducer2 == 'DMSO' "
    "& Metadata_Inhibitor == 'DMSO' "
    "& Metadata_Time == '1'"
)


# In[ ]:


train_df_list = []
# load in the the control well_fovs as a pandas dataframe
for well_fov, profile_path, train_test_split_path in tqdm.tqdm(
    zip(
        well_fov_profile_and_split_dict["well_fov"],
        well_fov_profile_and_split_dict["profile_path"],
        well_fov_profile_and_split_dict["train_test_split_path"],
    ),
    leave=False,
    total=len(well_fov_profile_and_split_dict["well_fov"]),
):
    if well_fov.split("_")[0] not in control_well_fovs:
        continue
    sc_tracks_df = pd.read_parquet(profile_path)
    # skip the profiles that do not contain DMSO as an inducer
    # we only want to load these to fit the normalization model
    train_test_split_df = pd.read_parquet(train_test_split_path)
    sc_tracks_df = sc_tracks_df.query(samples)
    sc_tracks_df = sc_tracks_df.loc[
        sc_tracks_df["analysis.included_at_least_one_outlier"] == False
    ]
    train_indices = train_test_split_df.loc[
        train_test_split_df["train_test_split"] == "train", "index"
    ]
    test_indices = train_test_split_df.loc[
        train_test_split_df["train_test_split"] == "test", "index"
    ]
    sc_tracks_df.reset_index(inplace=True, drop=False)
    train_df = sc_tracks_df.loc[sc_tracks_df["index"].isin(train_indices)]
    # we are concatenating a large amount of data but do not need all of it
    # to fit the normalization model
    # filter only the samples and train data needed here
    # set the metadata conditions to fit and apply normalization to
    train_df_list.append(train_df)
train_dmso_df = pd.concat(train_df_list, axis=0)
print(f"Loaded in {train_dmso_df.shape[0]} rows to normalize on")


# ## Normalize with standardize method with negative control on annotated data

# In[10]:


features = infer_cp_features(train_dmso_df, metadata=False)


# ## Fit the normalization model to the train data

# In[ ]:


norm_train_df = normalize(
    # df with annotated raw merged single cell features
    profiles=train_dmso_df,
    features=features,
    # specify samples used as normalization reference (negative control)
    samples=samples,
    # normalization method used
    method="standardize",
    transform_output_file=normalization_params_file_path,
)


# ## Apply the normalization to all splits now

# In[12]:


for well_fov, profile_path, train_test_split_path, norm_output_path in tqdm.tqdm(
    zip(
        well_fov_profile_and_split_dict["well_fov"],
        well_fov_profile_and_split_dict["profile_path"],
        well_fov_profile_and_split_dict["train_test_split_path"],
        well_fov_profile_and_split_dict["norm_output_path"],
    ),
    leave=False,
    total=len(well_fov_profile_and_split_dict["well_fov"]),
):
    if norm_output_path.exists():
        continue
    well_fov_df = pd.read_parquet(profile_path)

    # apply normalization
    subset_normalized_df = normalize(
        profiles=well_fov_df,
        features=features,
        method="standardize",
        fitted_transform_file=normalization_params_file_path,
        output_file=norm_output_path,
        output_type="parquet",
    )
