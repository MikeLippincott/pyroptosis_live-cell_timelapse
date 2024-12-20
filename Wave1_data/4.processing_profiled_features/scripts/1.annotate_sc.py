#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import json
import pathlib

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


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    "../../../data/raw/platemaps/wave1_plate_map.csv"
).resolve()
well_mapping_path = pathlib.Path("../../../data/processed/well_map.json").resolve(
    strict=True
)

# directory where parquet files are located
data_dir = pathlib.Path("../data/converted_data")

# directory where the annotated parquet files are saved to
output_dir = pathlib.Path("../data/annotated_data")
output_dir.mkdir(exist_ok=True)

well_number_to_name_map = json.load(open(well_mapping_path))


# In[3]:


# get a list of all files in the data directory
files = list(data_dir.glob("*.parquet"))
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

# In[4]:


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
    annotated_df["Metadata_Plate"] = data_run.split("_")[0]

    # move metadata well and single cell count to the front of the df (for easy visualization in python)
    well_column = annotated_df.pop("Metadata_Well")
    singlecell_column = annotated_df.pop("Metadata_number_of_singlecells")
    FOV_column = annotated_df.pop("Metadata_FOV")
    plate_column = annotated_df.pop("Metadata_Plate")
    # insert the column as the second index column in the dataframe
    annotated_df.insert(1, "Metadata_Well", well_column)
    annotated_df.insert(2, "Metadata_number_of_singlecells", singlecell_column)
    annotated_df.insert(3, "Metadata_FOV", FOV_column)
    annotated_df.insert(4, "Metadata_Plate", plate_column)

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

    time_mapping = {
        time: i
        for i, time in enumerate(annotated_df["Metadata_Plate"].sort_values().unique())
    }
    # check if the new columns exist, if so drop them
    if "Metadata_treatment_serum" in annotated_df.columns:
        annotated_df.drop(columns=["Metadata_treatment_serum"], inplace=True)
    if "Metadata_Time" in annotated_df.columns:
        annotated_df.drop(columns=["Metadata_Time"], inplace=True)
    # Combine all new columns at once to avoid fragmentation
    new_columns = pd.DataFrame(
        {
            "Metadata_treatment_serum": annotated_df["Metadata_treatment"]
            + " "
            + annotated_df["Metadata_serum"],
            "Metadata_Time": annotated_df["Metadata_Plate"].map(time_mapping),
        }
    )
    annotated_df = pd.concat([annotated_df, new_columns], axis=1)

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
