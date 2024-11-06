#!/usr/bin/env python
# coding: utf-8

# # Normalize annotated single cells using negative control

# ## Import libraries

# In[1]:


import pathlib

import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import output

# ## Set paths and variables

# In[2]:


# directory where combined parquet file are located
data_dir = pathlib.Path("../data/annotated_data_combined")

# directory where the normalized parquet file is saved to
output_dir = pathlib.Path("../data/normalized_data")
output_dir.mkdir(exist_ok=True)


# ## Define dict of paths

# In[3]:


# dictionary with each run for the cell type
dict_of_inputs = {
    "live_cell_pyroptosis_wave1_sc": {
        "combined_file_path": pathlib.Path(
            f"{data_dir}/live_cell_pyroptosis_wave1_sc.parquet"
        ).resolve(strict=True),
        "output_file_path": pathlib.Path(
            f"{output_dir}/live_cell_pyroptosis_wave1_sc_within_time_norm.parquet"
        ).resolve(),
    },
}


# ## Normalize with standardize method with negative control on annotated data

# The normalization needs to occur per time step.
# This code cell will split the data into time steps and normalize each time step separately.
# Then each normalized time step will be concatenated back together.

# In[ ]:


for info, input_path in dict_of_inputs.items():
    # read in the annotated file
    annotated_df = pd.read_parquet(input_path["combined_file_path"])
    annotated_df.reset_index(drop=True, inplace=True)
    # Normalize the single cell data per time point
    print(f"Shape of the annotated data: {annotated_df.shape}")
    # get unique time points (plates)
    plates = annotated_df.Metadata_Plate.unique()
    print(f"Unique time points: {plates}")
    output_dict_of_normalized_dfs = {}

    # define a for loop to normalize each time point
    for time_point in plates:
        # subset the data to the time point
        time_point_df = annotated_df.loc[annotated_df.Metadata_Plate == time_point]
        print(time_point_df.shape)
        # normalize annotated data
        normalized_df = normalize(
            # df with annotated raw merged single cell features
            profiles=time_point_df,
            # specify samples used as normalization reference (negative control)
            samples="Metadata_treatment == 'DMSO CTL'",
            # normalization method used
            method="standardize",
        )

        output_dict_of_normalized_dfs[time_point] = normalized_df

    # combine the normalized dataframes
    normalized_df = pd.concat(output_dict_of_normalized_dfs.values()).reset_index(
        drop=True
    )

    output(
        normalized_df,
        output_filename=input_path["output_file_path"],
        output_type="parquet",
    )
    print(f"Single cells have been normalized and saved to {pathlib.Path(info).name} !")
    # check to see if the features have been normalized
    print(normalized_df.shape)
    normalized_df.head()
