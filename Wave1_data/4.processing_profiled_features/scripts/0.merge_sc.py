#!/usr/bin/env python
# coding: utf-8

# # Merge single cells from CellProfiler outputs using CytoTable

# In[1]:


import argparse
import pathlib
import sys

import pandas as pd
from cytotable import convert, presets

sys.path.append("../../../utils")
import sc_extraction_utils as sc_utils
from parsl.config import Config
from parsl.executors import HighThroughputExecutor

# ## Set paths and variables
#
# All paths must be string but we use pathlib to show which variables are paths

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
    input_dir = pathlib.Path(
        "../../3.cellprofiling/analysis_output/W0052_F0001"
    ).resolve(strict=True)


# In[3]:


# type of file output from CytoTable (currently only parquet)
dest_datatype = "parquet"

# directory where parquet files are saved to
output_dir = pathlib.Path("../data/converted_data")
output_dir.mkdir(exist_ok=True, parents=True)


# In[4]:


# get the .sqlite file from the input directory
sqlite_file = list(input_dir.glob("*.sqlite"))[0]
dest_path = output_dir / str(sqlite_file.parent).split("/")[-1]
dest_path.mkdir(exist_ok=True, parents=True)
dest_path = dest_path / f"{sqlite_file.stem}.{dest_datatype}"
print(f"Destination path: {dest_path}")


# ## set config joins for each preset

# In[ ]:


# preset configurations based on typical CellProfiler outputs
preset = "cellprofiler_sqlite_pycytominer"
presets.config[preset][
    "CONFIG_JOINS"
    # remove Image_Metadata_Plate from SELECT as this metadata was not extracted from file names
    # add Image_Metadata_FOV as this is an important metadata when finding where single cells are located
] = """WITH Per_Image_Filtered AS (
                SELECT
                    Metadata_ImageNumber,
                    Image_Metadata_Time,
                    Image_Metadata_Well,
                    Image_Metadata_FOV,
                    Image_PathName_CL488,
                    Image_PathName_CL561,
                    Image_PathName_GSDM,
                    Image_PathName_BF,
                    Image_PathName_DNA,
                    Image_FileName_CL488,
                    Image_FileName_CL561,
                    Image_FileName_GSDM,
                    Image_FileName_BF,
                    Image_FileName_DNA,
                FROM
                    read_parquet('per_image.parquet')
                )
            SELECT
                *
            FROM
                Per_Image_Filtered AS per_image
            LEFT JOIN read_parquet('per_cytoplasm.parquet') AS per_cytoplasm ON
                per_cytoplasm.Metadata_ImageNumber = per_image.Metadata_ImageNumber
            LEFT JOIN read_parquet('per_cells.parquet') AS per_cells ON
                per_cells.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_cells.Metadata_Cells_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Cells
            LEFT JOIN read_parquet('per_nuclei.parquet') AS per_nuclei ON
                per_nuclei.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_nuclei.Metadata_Nuclei_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Nuclei
            """


# ## Convert SQLite file and merge single cell objects into parquet file
#
# This was not run to completion as we use the nbconverted python file for full run.

# In[6]:


# merge single cells and output as parquet file
convert(
    source_path=sqlite_file,
    dest_path=dest_path,
    dest_datatype=dest_datatype,
    preset=preset,
    parsl_config=Config(
        executors=[HighThroughputExecutor()],
    ),
    chunk_size=1000,
)


# In[7]:


print(f"Merged and converted {pathlib.Path(dest_path).name}!")
print(f"Saved to {dest_path}")
df = pd.read_parquet(dest_path)
df["Metadata_Well_Time"] = df["Image_Metadata_Well"] + "_" + df["Image_Metadata_Time"]
print(f"Shape of {pathlib.Path(dest_path).name}: {df.shape}")
df.head()


# In[ ]:


Metadata_number_of_singlecells_df = (
    df.groupby("Metadata_Well_Time")
    .value_counts()
    .reset_index(name="Metadata_number_of_singlecells")
)
# merge the number of single cells with the original dataframe
df = df.merge(
    Metadata_number_of_singlecells_df, on=["Metadata_Well_Time", "Metadata_Well_Time"]
)
df.head()


# In[9]:


# cast to int
df["Metadata_number_of_singlecells"] = df["Metadata_number_of_singlecells"].astype(int)
df.to_parquet(dest_path)

print(f"Shape of {pathlib.Path(dest_path).name}: {df.shape}")
print(f"Added single cell count as metadata to {pathlib.Path(dest_path).name}!")


# In[10]:


df.head()
