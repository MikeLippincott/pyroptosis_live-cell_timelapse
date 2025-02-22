#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import argparse
import json
import pathlib
import sys

import lancedb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pycytominer import annotate
from pycytominer.cyto_utils import output


# ## Set paths and variables
# ### Relate the CellProfiler output to the platemap file

# In[2]:


# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False

if not in_notebook:
    print("Running as script")
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--input_dir",
        type=str,
        help="Path to the input directory containing the tiff images",
    )

    args = parser.parse_args()
    input_dir = pathlib.Path(args.input_dir).resolve(strict=True)
else:
    print("Running in a notebook")
    input_dir = pathlib.Path("../data/converted_data/W0052_F0001").resolve(strict=True)


# In[3]:


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    "../../../data/processed/platemaps/wave1_plate_map.csv"
).resolve()
well_mapping_path = pathlib.Path("../../../data/processed/well_map.json").resolve(
    strict=True
)


# directory where the annotated parquet files are saved to
output_dir = pathlib.Path(f"../data/annotated_data/{input_dir.stem}")
output_dir.mkdir(exist_ok=True, parents=True)

well_number_to_name_map = json.load(open(well_mapping_path))


# In[4]:


# get a list of all files in the data directory
files = list(input_dir.glob("*.parquet"))
dict_of_inputs = {}
for file in files:
    file_name = file.stem
    print(f"Processing {file_name}")
    dict_of_inputs[file_name] = {
        "source_path": f"{file}",
        "platemap_file_path": f"{platemap_path}",
    }
print(f"Processing {len(dict_of_inputs.keys())} files")


# ## Annotate merged single cells

# In[5]:


for data_run, info in dict_of_inputs.items():
    # load in converted parquet file as df to use in annotate function
    single_cell_df = pd.read_parquet(info["source_path"])

    # map the well to the well_map
    single_cell_df["Image_Metadata_Well"] = single_cell_df["Image_Metadata_Well"].map(
        well_number_to_name_map
    )

    platemap_df = pd.read_csv(info["platemap_file_path"])

    output_file = str(pathlib.Path(f"{output_dir}/{data_run}_sc.parquet"))

    # add metadata from platemap file to extracted single cell features
    annotated_df = annotate(
        profiles=single_cell_df,
        platemap=platemap_df,
        join_on=["Metadata_well", "Image_Metadata_Well"],
    )
    annotated_df.rename(columns={"Image_Metadata_FOV": "Metadata_FOV"}, inplace=True)

    # move metadata well and single cell count to the front of the df (for easy visualization in python)
    well_column = annotated_df.pop("Metadata_Well")
    singlecell_column = annotated_df.pop("Metadata_number_of_singlecells")
    FOV_column = annotated_df.pop("Metadata_FOV")
    time_column = annotated_df.pop("Image_Metadata_Time")
    # insert the column as the second index column in the dataframe
    annotated_df.insert(1, "Metadata_Well", well_column)
    annotated_df.insert(2, "Metadata_number_of_singlecells", singlecell_column)
    annotated_df.insert(3, "Metadata_FOV", FOV_column)
    annotated_df.insert(5, "Metadata_Time", time_column)
    # rename metadata columns to match the expected column names
    columns_to_rename = {
        "Nuclei_Location_Center_Y": "Metadata_Nuclei_Location_Center_Y",
        "Nuclei_Location_Center_X": "Metadata_Nuclei_Location_Center_X",
    }
    # Image_FileName cols
    for col in annotated_df.columns:
        if "Image_FileName" in col:
            columns_to_rename[col] = f"Metadata_{col}"
        elif "Image_PathName" in col:
            columns_to_rename[col] = f"Metadata_{col}"
        elif "TrackObjects" in col:
            columns_to_rename[col] = f"Metadata_{col}"
    # rename metadata columns
    annotated_df.rename(columns=columns_to_rename, inplace=True)
    # check if the new columns exist, if so drop them
    if "Metadata_treatment_serum" in annotated_df.columns:
        annotated_df.drop(columns=["Metadata_treatment_serum"], inplace=True)

    # save annotated df as parquet file
    output(
        df=annotated_df,
        output_filename=output_file,
        output_type="parquet",
    )
    # check last annotated df to see if it has been annotated correctly
    print(f"{data_run} has been annotated")
    print(f"With the input shape of {single_cell_df.shape}")
    print(f"Output shape of {annotated_df.shape}")
annotated_df.head()

