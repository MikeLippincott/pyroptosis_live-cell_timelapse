#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import argparse
import os
import pathlib

import natsort
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

# In[2]:


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


# In[3]:


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/plate_2/platemap.csv"
).resolve()

image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
qc_profiles_path = pathlib.Path(
    f"{image_base_dir}/7.qc_profiles/{plate_name}/"
).resolve(strict=True)

annotated_profiles_path = pathlib.Path(
    f"{image_base_dir}/8.annotated_profiles/{plate_name}/"
).resolve()
annotated_profiles_path.mkdir(exist_ok=True, parents=True)


# ## Annotate merged single cells

# In[4]:


qc_profiles_path_files = natsort.natsorted(
    list(qc_profiles_path.glob("*.parquet")), key=lambda x: x.name
)
print(f"Found {len(qc_profiles_path_files)} QC profiles")


# In[5]:


platemap_df = pd.read_csv(platemap_path)
# remove the leading zero from the well column in the platemap
platemap_df["Metadata_Well"] = platemap_df["Metadata_Well"].str.replace("0", "")


# In[ ]:


for qc_profiles_path in tqdm.tqdm(
    qc_profiles_path_files,
    desc="Annotating profiles",
    total=len(qc_profiles_path_files),
    unit="file",
):
    annotated_profile_path_output = pathlib.Path(
        f"{annotated_profiles_path}/{qc_profiles_path.stem.replace('qc', 'annotated')}.parquet"
    ).resolve()
    if annotated_profile_path_output.exists():
        continue
    single_cell_df = pd.read_parquet(qc_profiles_path)

    # add metadata from platemap file to extracted single cell features
    annotated_df = annotate(
        profiles=single_cell_df,
        platemap=platemap_df,
        join_on=["Metadata_Well", "Metadata_Well"],
        output_file=annotated_profile_path_output,
        output_type="parquet",
    )
