#!/usr/bin/env python
# coding: utf-8

# # Aggregate the single-cell profiles to the well level
# This notebook is not run as a large amount of RAM is needed to run it. It is provided for reference only.

# In[1]:


import pathlib

import pandas as pd
import pycytominer


# In[2]:


# directory where combined parquet file are located
data_dir = pathlib.Path("../data")
aggregate_dir = pathlib.Path("../data/aggregated")
aggregate_dir.mkdir(exist_ok=True, parents=True)


# In[3]:


# dictionary with each run for the cell type
dict_of_inputs = {
    "first_time": {
        "normalized": pathlib.Path(
            f"{data_dir}/normalized_data/live_cell_pyroptosis_wave1_sc_first_time_norm.parquet"
        ).resolve(strict=True),
        "selected": pathlib.Path(
            f"{data_dir}/feature_selected_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
        ).resolve(strict=True),
        "aggregate_normalized": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_first_time_norm_agg.parquet"
        ).resolve(),
        "aggregate_selected": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"
        ).resolve(),
    },
    "pan_time": {
        "normalized": pathlib.Path(
            f"{data_dir}/normalized_data/live_cell_pyroptosis_wave1_sc_pan_time_norm.parquet"
        ).resolve(strict=True),
        "selected": pathlib.Path(
            f"{data_dir}/feature_selected_data/live_cell_pyroptosis_wave1_sc_pan_time_norm_fs.parquet"
        ).resolve(strict=True),
        "aggregate_normalized": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_pan_time_norm_agg.parquet"
        ).resolve(),
        "aggregate_selected": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_pan_time_norm_fs_agg.parquet"
        ).resolve(),
    },
    "within_time": {
        "normalized": pathlib.Path(
            f"{data_dir}/normalized_data/live_cell_pyroptosis_wave1_sc_within_time_norm.parquet"
        ).resolve(strict=True),
        "selected": pathlib.Path(
            f"{data_dir}/feature_selected_data/live_cell_pyroptosis_wave1_sc_within_time_norm_fs.parquet"
        ).resolve(strict=True),
        "aggregate_normalized": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_within_time_norm_agg.parquet"
        ).resolve(),
        "aggregate_selected": pathlib.Path(
            f"{aggregate_dir}/live_cell_pyroptosis_wave1_within_time_norm_fs_agg.parquet"
        ).resolve(),
    },
}


# The cell below must be run as a script on an HPC cluster with sufficient memory.

# In[ ]:


for profile in dict_of_inputs.keys():

    # Load the normalized data
    norm_df = pd.read_parquet(dict_of_inputs[profile]["normalized"])

    norm_aggregate_df = pycytominer.aggregate(
        population_df=norm_df,
        strata=["Metadata_Well", "Metadata_Time"],
        features="infer",
        operation="median",
    )
    print(f"Normalized data shape: {norm_df.shape}")
    print(f"Aggregated normalized data shape: {norm_aggregate_df.shape}")

    # Save the aggregated normalized data
    norm_aggregate_df.to_parquet(dict_of_inputs[profile]["aggregate_normalized"])
    del norm_df, norm_aggregate_df

    # Load the selected data
    norm_fs_df = pd.read_parquet(dict_of_inputs[profile]["selected"])

    norm_fs_aggregate_df = pycytominer.aggregate(
        population_df=norm_fs_df,
        strata=["Metadata_Well", "Metadata_Time"],
        features="infer",
        operation="median",
    )
    print(f"Selected data shape: {norm_fs_df.shape}")
    print(f"Aggregated selected data shape: {norm_fs_aggregate_df.shape}")

    # Save the aggregated selected data
    norm_fs_aggregate_df.to_parquet(dict_of_inputs[profile]["aggregate_selected"])
    del norm_fs_df, norm_fs_aggregate_df

