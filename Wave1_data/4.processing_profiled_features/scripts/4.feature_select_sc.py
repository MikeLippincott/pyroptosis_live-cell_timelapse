#!/usr/bin/env python
# coding: utf-8

# # Perform feature selection on normalized data

# ## Import libraries

# In[1]:


import gc
import pathlib

import pandas as pd
from pycytominer import feature_select
from pycytominer.cyto_utils import output

# ## Set paths and variables

# In[2]:


# directory where combined parquet file are located
data_dir = pathlib.Path("../data/normalized_data/")

# directory where the normalized parquet file is saved to
output_dir = pathlib.Path("../data/feature_selected_data")
output_dir.mkdir(exist_ok=True, parents=True)


# ## Define dict of paths

# In[3]:


# dictionary with each run for the cell type
dict_of_inputs = {
    "live_cell_pyroptosis_wave1_sc_first_time_norm": {
        "normalized_df_path": pathlib.Path(
            f"{data_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm.parquet"
        ).resolve(strict=True),
        "output_file_path": pathlib.Path(
            f"{output_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
        ).resolve(),
    },
}


# ## Perform feature selection

# In[4]:


# define operations to be performed on the data
# list of operations for feature select function to use on input profile
feature_select_ops = [
    "variance_threshold",
    "blocklist",
    "drop_na_columns",
    "correlation_threshold",
]


# In[ ]:


manual_block_list = [
    "Nuclei_AreaShape_BoundingBoxArea",
    "Nuclei_AreaShape_BoundingBoxMinimum_X",
    "Nuclei_AreaShape_BoundingBoxMinimum_Y",
    "Nuclei_AreaShape_BoundingBoxMaximum_X",
    "Nuclei_AreaShape_BoundingBoxMaximum_Y",
    "Cells_AreaShape_BoundingBoxArea",
]


# This last cell does not get run due to memory constraints.
# It is run on an HPC cluster with more memory available.

# In[ ]:


# feature selection parameters
print("Performing feature selection on normalized annotated merged single cells!")
for info, input_path in dict_of_inputs.items():
    # read in the annotated file
    normalized_df = pd.read_parquet(input_path["normalized_df_path"])
    metadata_cols = [x for x in normalized_df.columns if x.startswith("Metadata_")]
    normalized_features_df = normalized_df.drop(metadata_cols, axis="columns")
    # perform feature selection with the operations specified
    feature_select_df = feature_select(
        normalized_features_df,
        operation=feature_select_ops,
    )

    # add "Metadata_" to the beginning of each column name in the list
    feature_select_df.columns = [
        "Metadata_" + column if column in manual_block_list else column
        for column in feature_select_df.columns
    ]
    # add metadata columns back to the feature selected df
    feature_select_df = pd.concat(
        [normalized_df[metadata_cols], feature_select_df], axis="columns"
    )
    print("Feature selection complete, saving to parquet file!")
    # save features selected df as parquet file
    output(
        df=feature_select_df,
        output_filename=input_path["output_file_path"],
        output_type="parquet",
    )
    print(
        f"Features have been selected for PBMC cells and saved to {pathlib.Path(info).name}!"
    )
    # check to see if the shape of the df has changed indicating feature selection occurred
    print(feature_select_df.shape)
    feature_select_df.head()
