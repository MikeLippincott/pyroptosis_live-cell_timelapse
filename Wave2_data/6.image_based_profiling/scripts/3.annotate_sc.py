#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import argparse
import os
import pathlib

import pandas as pd
from pycytominer import annotate
from pycytominer.cyto_utils import output
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


# ## Set paths and variables
# ### Relate the CellProfiler output to the platemap file

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


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/platemap.csv"
).resolve()

image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
qc_profiles_path = pathlib.Path(
    f"{image_base_dir}/7.qc_profiles/{plate_name}/qc_profiles.parquet"
).resolve(strict=True)

annotated_profiles_path = pathlib.Path(
    f"{image_base_dir}/8.annotated_profiles/{plate_name}/annotated_profiles.parquet"
).resolve()
annotated_profiles_path.parent.mkdir(exist_ok=True)


# ## Annotate merged single cells

# In[3]:


# load in converted parquet file as df to use in annotate function
single_cell_df = pd.read_parquet(qc_profiles_path)

platemap_df = pd.read_csv(platemap_path)


# add metadata from platemap file to extracted single cell features
annotated_df = annotate(
    profiles=single_cell_df,
    platemap=platemap_df,
    join_on=["Metadata_Well", "Metadata_Well"],
)


# In[4]:


# check after annotation to verify row alignment,
# identify duplicate columns,
# or detect any newly introduced null values.
if annotated_df.shape[0] != single_cell_df.shape[0]:
    print(
        "Warning: Number of rows in the annotated dataframe does not match the original single cell dataframe."
    )
if annotated_df.shape[1] <= single_cell_df.shape[1]:
    print(
        "Warning: No new columns were added during annotation, or some columns may have been dropped."
    )
if single_cell_df.isnull().any().any():
    print(
        "Warning: Null values detected in the original single cell dataframe before annotation."
    )
if annotated_df.isnull().any().any():
    print("Warning: Null values detected in the annotated dataframe after annotation.")


# In[5]:


# save annotated df as parquet file
output(
    df=annotated_df,
    output_filename=annotated_profiles_path,
    output_type="parquet",
)

annotated_df.head()
