#!/usr/bin/env python
# coding: utf-8

# # Run QC on raw single cell profiles

# ## Import libraries

# In[1]:


import logging
import os
import pathlib

import cosmicqc
import natsort
import numpy as np
import pandas as pd
import polars as pl
from cytodataframe import CytoDataFrame
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm


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


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
combined_profiles_path = image_base_dir / "6.combined_profiles" / plate_name
qc_path = image_base_dir / "7.qc_profiles" / plate_name
qc_path.mkdir(parents=True, exist_ok=True)


# In[4]:


needed_metadata_cols = [
    "Metadata_Well",
    "Metadata_Time",
    "Metadata_Well_FOV",
    "Metadata_FOV",
    "Metadata_Well_FOV_Time",
    "Metadata_Nuclei_Number_Object_Number",
    "Metadata_Cells_Number_Object_Number",
    "Metadata_Cytoplasm_Parent_Nuclei",
    "Metadata_Cytoplasm_Parent_Cells",
]
features_of_interest = [
    "Nuclei_AreaShape_Area",
    "Nuclei_AreaShape_FormFactor",
    "Nuclei_AreaShape_Eccentricity",
]


# In[ ]:


list_of_dfs = []
for file_path in tqdm.tqdm(
    combined_profiles_path.glob("*.parquet"),
    total=len(list(combined_profiles_path.glob("*.parquet"))),
    desc="Processing combined profiles",
    unit="file",
    leave=True,
):

    list_of_dfs.append(
        pd.read_parquet(file_path, columns=needed_metadata_cols + features_of_interest)
    )
    df = pd.concat(list_of_dfs, axis=0, ignore_index=True)

num_na_rows = df.isna().any(axis=1).sum()
print(f"Number of rows with NaN values: {num_na_rows}")
df.dropna(inplace=True)
df.insert(
    0,
    "Metadata_unique_cell_id",
    (
        df["Metadata_Well_FOV_Time"].astype(str)
        + "_"
        + df["Metadata_Nuclei_Number_Object_Number"].astype(int).astype(str)
    ),
)
duplicated_df = df[df.duplicated(subset=["Metadata_unique_cell_id"])]
# drop the duplicates, retain neither of the duplicates
df = df.drop_duplicates(subset=["Metadata_unique_cell_id"], keep=False)
# find duplicates based on the unique cell identifier
print(f"Number of rows after dropping duplicates: {len(df):,}")


# In[6]:


metadata_cols = [x for x in df.columns if "Metadata_" in x]
feature_cols = [x for x in df.columns if "Metadata_" not in x]


# In[7]:


features_of_interest = [
    "Nuclei_AreaShape_Area",
    "Nuclei_AreaShape_FormFactor",
    "Nuclei_AreaShape_Eccentricity",
]
df_merged_single_cells = df[metadata_cols + features_of_interest].copy()

# establish outliers in the single-cell profiles by using qc thresholds defined in cosmicqc
cosmicqc.analyze.identify_outliers(
    df=df_merged_single_cells,
    # metadata_columns=metadata_cols,
    feature_thresholds={"Nuclei_AreaShape_Area": 1},
)
cosmicqc.analyze.find_outliers(
    df=df_merged_single_cells,
    metadata_columns=metadata_cols,
    feature_thresholds={"Nuclei_AreaShape_FormFactor": 1},
)
cosmicqc.analyze.find_outliers(
    df=df_merged_single_cells,
    metadata_columns=metadata_cols,
    feature_thresholds={"Nuclei_AreaShape_Eccentricity": 1},
)

# label outliers in the single-cell profiles by using qc thresholds defined in cosmicqc
df_labeled_outliers = cosmicqc.analyze.label_outliers(
    df=df_merged_single_cells,
    include_threshold_scores=True,
)

# create a column which indicates whether an erroneous outlier was detected
df_labeled_outliers["analysis.included_at_least_one_outlier"] = df_labeled_outliers[
    [col for col in df_labeled_outliers.columns.tolist() if ".is_outlier" in col]
].any(axis=1)
df_labeled_outliers = pd.DataFrame(df_labeled_outliers)


# Remove for now - error in the CP pipeline.
# CP does not respect object IDs - must generate the cytoplasm masks external and rerun.
# This will be okay for now to get preliminary data.

# In[8]:


outliers_counts = df_labeled_outliers[
    "analysis.included_at_least_one_outlier"
].value_counts()


# In[9]:


df_labeled_outliers.rename(
    columns={
        x: x.replace("cqc", "Metadata_cqc")
        for x in df_labeled_outliers.columns
        if "cqc" in x
    },
    inplace=True,
)


# In[10]:


# show the percentage of total dataset
print(
    np.round((outliers_counts.iloc[1] / outliers_counts.iloc[0]) * 100, 2),
    "%",
    "of",
    outliers_counts.iloc[0],
    "include erroneous outliers of some kind.",
)


# In[11]:


for file_path in tqdm.tqdm(
    combined_profiles_path.glob("*.parquet"),
    total=len(list(combined_profiles_path.glob("*.parquet"))),
    desc="Processing combined profiles",
    unit="file",
    leave=True,
):
    qc_file_path = qc_path / f"{file_path.stem}_qc.parquet"
    well_fov_df = pd.read_parquet(file_path)

    # well_fov_df.dropna(inplace=True)
    well_fov_df.insert(
        0,
        "Metadata_unique_cell_id",
        (
            well_fov_df["Metadata_Well_FOV_Time"].astype(str)
            + "_"
            + well_fov_df["Metadata_Nuclei_Number_Object_Number"].astype(str)
        ),
    )
    duplicated_df = well_fov_df[
        well_fov_df.duplicated(subset=["Metadata_unique_cell_id"])
    ]
    # drop the duplicates, retain neither of the duplicates
    well_fov_df = well_fov_df.drop_duplicates(
        subset=["Metadata_unique_cell_id"], keep=False
    )
    well_fov_df.reset_index(drop=True, inplace=True)
    common_columns = list(
        set(df_labeled_outliers.columns).intersection(set(well_fov_df.columns))
    )

    tmp_df = pd.merge(
        left=well_fov_df,
        right=df_labeled_outliers,
        how="left",
        on=common_columns,
    )
    tmp_df.to_parquet(qc_file_path, index=False)
