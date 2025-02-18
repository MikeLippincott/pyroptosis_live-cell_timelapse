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


# In[ ]:


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
}


# The cell below must be run as a script on an HPC cluster with sufficient memory.

# In[4]:


sc_metadata_cols_to_drop = [
    "Metadata_ImageNumber",
    "Metadata_Cells_Number_Object_Number",
    "Metadata_Cytoplasm_Parent_Cells",
    "Metadata_Cytoplasm_Parent_Nuclei",
    "Metadata_ImageNumber_1",
    "Metadata_ImageNumber_2",
    "Metadata_ImageNumber_3",
    "Metadata_Nuclei_Number_Object_Number",
    "Metadata_Image_FileName_BF",
    "Metadata_Image_FileName_CL488",
    "Metadata_Image_FileName_CL561",
    "Metadata_Image_FileName_DNA",
    "Metadata_Image_FileName_GSDM",
    "Metadata_Image_PathName_BF",
    "Metadata_Image_PathName_CL488",
    "Metadata_Image_PathName_CL561",
    "Metadata_Image_PathName_DNA",
    "Metadata_Image_PathName_GSDM",
    "Metadata_Nuclei_Location_Center_X",
    "Metadata_Nuclei_Location_Center_Y",
    "Metadata_number_of_singlecells",
    "Metadata_FOV",
]


# In[5]:


for profile in dict_of_inputs.keys():

    ###########################################################################################
    # Normalized data
    ###########################################################################################
    # Load the normalized data
    norm_df = pd.read_parquet(dict_of_inputs[profile]["normalized"])
    metadata_cols = [cols for cols in norm_df.columns if "Metadata" in cols]
    features_cols = [cols for cols in norm_df.columns if "Metadata" not in cols]

    norm_aggregate_df = pycytominer.aggregate(
        population_df=norm_df,
        strata=["Metadata_Well", "Metadata_Time"],
        features=features_cols,
        operation="median",
    )
    # Drop metadata columns
    metadata_cols = [x for x in metadata_cols if x not in sc_metadata_cols_to_drop]
    metadata_df = norm_df[metadata_cols]
    metadata_df = metadata_df.drop_duplicates()
    norm_aggregate_df = pd.merge(
        metadata_df, norm_aggregate_df, on=["Metadata_Well", "Metadata_Time"]
    )
    print(f"Normalized data shape: {norm_df.shape}")
    print(f"Aggregated normalized data shape: {norm_aggregate_df.shape}")

    # Save the aggregated normalized data
    norm_aggregate_df.to_parquet(dict_of_inputs[profile]["aggregate_normalized"])
    del norm_df, norm_aggregate_df
    ###########################################################################################
    # Selected data
    ###########################################################################################
    # Load the selected data
    norm_fs_df = pd.read_parquet(dict_of_inputs[profile]["selected"])
    metadata_cols = [cols for cols in norm_fs_df.columns if "Metadata" in cols]
    features_cols = [cols for cols in norm_fs_df.columns if "Metadata" not in cols]

    norm_fs_aggregate_df = pycytominer.aggregate(
        population_df=norm_fs_df,
        strata=["Metadata_Well", "Metadata_Time"],
        features=features_cols,
        operation="median",
    )
    # Drop metadata columns
    metadata_cols = [x for x in metadata_cols if x not in sc_metadata_cols_to_drop]
    metadata_df = norm_fs_df[metadata_cols]
    metadata_df = metadata_df.drop_duplicates()
    norm_fs_aggregate_df = pd.merge(
        metadata_df, norm_fs_aggregate_df, on=["Metadata_Well", "Metadata_Time"]
    )
    print(f"Normalized data shape: {norm_fs_df.shape}")
    print(f"Aggregated normalized data shape: {norm_fs_aggregate_df.shape}")

    # Save the aggregated selected data
    norm_fs_aggregate_df.to_parquet(dict_of_inputs[profile]["aggregate_selected"])
    del norm_fs_df, norm_fs_aggregate_df
