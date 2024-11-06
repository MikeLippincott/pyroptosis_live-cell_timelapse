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
            f"{output_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm.parquet"
        ).resolve(),
    },
}


# ## Normalize with standardize method with negative control on annotated data

# The normalization needs to occur per time step.
# This code cell will split the data into time steps and normalize each time step separately.
# Then each normalized time step will be concatenated back together.

# In[5]:


for info, input_path in dict_of_inputs.items():
    # read in the annotated file
    print(input_path)
    annotated_df = pd.read_parquet(input_path["combined_file_path"])
    annotated_df.reset_index(drop=True, inplace=True)
    # Normalize the single cell data per time point
    print(f"Shape of the annotated data: {annotated_df.shape}")
    normalized_df = normalize(
        # df with annotated raw merged single cell features
        profiles=annotated_df,
        # specify samples used as normalization reference (negative control)
        samples="Metadata_treatment == 'DMSO CTL' & Metadata_Plate == '20241024T194653'",
        # normalization method used
        method="standardize",
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
