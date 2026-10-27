#!/usr/bin/env python
# coding: utf-8

# # Perform feature selection on normalized data

# ## Import libraries

# In[1]:


import argparse
import json
import os
import pathlib

import natsort
import pandas as pd
import pyarrow.parquet as pq
from pycytominer import feature_select
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
platemap_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/{plate_name}/platemap.csv"
).resolve()

image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
normalized_profiles_path = pathlib.Path(
    f"{image_base_dir}/10.normalized_profiles/{plate_name}/"
).resolve(strict=True)

train_test_split_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/train_test_split_indices/{plate_name}/"
).resolve()

feature_selected_profiles_path = pathlib.Path(
    f"{image_base_dir}/11.feature_selected_profiles/{plate_name}/"
).resolve()
feature_selected_profiles_path.mkdir(exist_ok=True, parents=True)
feature_select_cols_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/notebooks/feature_select_cols.json"
).resolve()
if feature_select_cols_path.exists():
    feature_select_cols_path.unlink()


# ## Define dict of paths

# ## Perform feature selection

# In[4]:


# define operations to be performed on the data
# list of operations for feature select function to use on input profile
feature_select_ops = [
    "variance_threshold",
    "blocklist",
    "drop_na_columns",
    "correlation_threshold",
    "drop_outliers",
]


# In[5]:


well_fov_profile_and_split_dict = {
    "well_fov": [],
    "profile_path": [],
    "train_test_split_path": [],
    "fs_output_path": [],
}
# load each of the control_well_fovs train test split indices as a pandas dataframe
train_test_split_path_list = natsort.natsorted(
    list(train_test_split_path.glob("*.parquet")), key=lambda x: x.name
)


# In[6]:


norm_profiles_path_list = natsort.natsorted(
    list(normalized_profiles_path.glob("*.parquet")), key=lambda x: x.name
)
print(f"Found {len(norm_profiles_path_list)} normalized profiles for {plate_name}")


# In[7]:


# load in the the control well_fovs as a pandas dataframe
norm_profiles_path_list = list(normalized_profiles_path.glob("*.parquet"))
norm_profiles_path_list = natsort.natsorted(
    norm_profiles_path_list, key=lambda x: x.stem
)

for norm_profile_path in tqdm.tqdm(norm_profiles_path_list):
    well_fov = norm_profile_path.stem.replace("_normalized", "")
    # check if well_fov is in the well_fov_profile_and_split_dict
    if (
        well_fov not in well_fov_profile_and_split_dict["well_fov"]
        and norm_profile_path not in well_fov_profile_and_split_dict["profile_path"]
    ):
        well_fov_profile_and_split_dict["well_fov"].append(well_fov)
        well_fov_profile_and_split_dict["profile_path"].append(norm_profile_path)
    elif (
        well_fov in well_fov_profile_and_split_dict["well_fov"]
        and norm_profile_path not in well_fov_profile_and_split_dict["profile_path"]
    ):
        # find the index of the well_fov in the well_fov_profile_and_split_dict
        index = well_fov_profile_and_split_dict["well_fov"].index(well_fov)
        well_fov_profile_and_split_dict["profile_path"][index] = norm_profile_path
    output_path = pathlib.Path(
        f"{feature_selected_profiles_path}/{well_fov}_fs.parquet"
    )
    well_fov_profile_and_split_dict["fs_output_path"].append(output_path)
    well_fov_profile_and_split_dict["train_test_split_path"].append(None)

for sc_split in tqdm.tqdm(train_test_split_path_list):
    well_fov = sc_split.stem.replace("_train_test_split", "")
    if well_fov in well_fov_profile_and_split_dict["well_fov"]:
        index = well_fov_profile_and_split_dict["well_fov"].index(well_fov)
        well_fov_profile_and_split_dict["train_test_split_path"][index] = sc_split
well_fov_profile_and_split_dict


# In[8]:


train_df_list = []
for well_fov, profile_path, train_test_split_path, fs_output_path in tqdm.tqdm(
    zip(
        well_fov_profile_and_split_dict["well_fov"],
        well_fov_profile_and_split_dict["profile_path"],
        well_fov_profile_and_split_dict["train_test_split_path"],
        well_fov_profile_and_split_dict["fs_output_path"],
    ),
    total=len(well_fov_profile_and_split_dict["well_fov"]),
):
    splits_df = pd.read_parquet(train_test_split_path)
    profile_df = pd.read_parquet(profile_path)
    train_indices = splits_df.loc[splits_df["train_test_split"] == "train", "index"]
    test_indices = splits_df.loc[splits_df["train_test_split"] == "test", "index"]
    profile_df.reset_index(inplace=True, drop=False)
    train_df = profile_df.loc[profile_df["index"].isin(train_indices)]
    if profile_df.shape[0] != train_df.shape[0] + len(test_indices):
        raise ValueError("Train and test split does not match the original dataframe")
    train_df_list.append(train_df)
train_df = pd.concat(train_df_list, ignore_index=True)
print(f"Loaded in {train_df.shape[0]} rows to feature select on for {plate_name}")
print(
    f"Initially found {len([x for x in train_df.columns if not x.startswith('Metadata_')])} feature columns in the training data for {plate_name}"
)


# In[9]:


# apply the feature selection to the training dataframe
features = infer_cp_features(train_df)
metadata_cols = [col for col in train_df.columns if col not in features]
normalized_features_df = train_df.drop(metadata_cols, axis="columns")
# perform feature selection with the operations specified
feature_select_df = feature_select(
    normalized_features_df,
    operation=feature_select_ops,
)
# get the cols that remain
feature_selected_cols = feature_select_df.columns
print(
    f"After feature selection, found {len(feature_selected_cols)} feature columns in the training data for {plate_name}"
)
# save the cols to an intermediate file
with open(feature_select_cols_path, "w") as f:
    json.dump(feature_selected_cols.tolist(), f)


# In[10]:


# apply the feature selection to all dataframes
for well_fov, profile_path, fs_output_path in tqdm.tqdm(
    zip(
        well_fov_profile_and_split_dict["well_fov"],
        well_fov_profile_and_split_dict["profile_path"],
        well_fov_profile_and_split_dict["fs_output_path"],
    ),
    total=len(well_fov_profile_and_split_dict["well_fov"]),
):

    if fs_output_path.exists():
        continue
    column_names = pq.read_schema(profile_path).names
    metadata_cols = [col for col in column_names if col.startswith("Metadata_")]
    columns_to_keep = metadata_cols + list(feature_selected_cols)
    profile_df = pd.read_parquet(profile_path, columns=columns_to_keep)
    profile_df.to_parquet(fs_output_path, index=False)
