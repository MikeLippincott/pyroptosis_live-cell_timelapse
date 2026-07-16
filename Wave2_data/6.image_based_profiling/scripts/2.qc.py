#!/usr/bin/env python
# coding: utf-8

# # Run QC on raw single cell profiles

# ## Import libraries

# In[3]:


import logging
import os
import pathlib

import cosmicqc
import natsort
import numpy as np
import pandas as pd
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

# In[ ]:


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


# In[ ]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = root_dir / "data"
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
combined_profiles_path = image_base_dir / "6.combined_profiles" / plate_name
qc_path = image_base_dir / "7.qc_profiles" / plate_name
qc_path.mkdir(parents=True, exist_ok=True)


# In[5]:


for file_path in tqdm.tqdm(
    combined_profiles_path.glob("*.parquet"),
    desc="Processing combined profiles",
    unit="file",
    leave=True,
):
    file_path_stem = file_path.stem
    qc_output_path = qc_path / f"{file_path_stem}_qc.parquet"
    continue


# In[6]:


file_path


# In[13]:


df = pd.read_parquet(file_path)


# In[ ]:


df[df.columns[df.isna().sum() > 0].tolist()]
df[[x for x in df.columns if "metadata" in x.lower()]]


# In[ ]:


df = pd.read_parquet(file_path)
metadata_cols = [x for x in df.columns if "Metadata_" in x]
feature_cols = [x for x in df.columns if "Metadata_" not in x]
features_of_interest = [
    "Nuclei_AreaShape_Area",
    "Nuclei_AreaShape_FormFactor",
    "Nuclei_AreaShape_Eccentricity",
]
df_merged_single_cells = df[metadata_cols + features_of_interest].copy()

# establish outliers in the single-cell profiles by using qc thresholds defined in cosmicqc
cosmicqc.analyze.identify_outliers(
    df=df_merged_single_cells,
    metadata_columns=metadata_cols,
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


# In[9]:


df_labeled_outliers = df_labeled_outliers["analysis.included_at_least_one_outlier"]
outliers_counts = df_labeled_outliers.value_counts()
outliers_counts


# In[11]:


outliers_counts.iloc[0]


# In[12]:


# show the percentage of total dataset
print(
    np.round((outliers_counts.iloc[1] / outliers_counts.iloc[0]) * 100, 2),
    "%",
    "of",
    outliers_counts.iloc[0],
    "include erroneous outliers of some kind.",
)


# In[ ]:


before_shape = df.shape
# df = df.iloc[df_labeled_outliers.index[df_labeled_outliers == False], :]
df = df.loc[~df_labeled_outliers]
print(
    f"Prior to qc we had {before_shape[0]} rows and after removing outliers we have {df.shape[0]} rows."
)


# In[ ]:


df.to_parquet(qc_profiles_path, index=False)


# In[ ]:


df.head()
