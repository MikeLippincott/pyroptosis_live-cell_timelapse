#!/usr/bin/env python
# coding: utf-8

# This is a place holder for merging single-cell tracks with the profiles

# In[1]:


import os
import pathlib
import shutil

import natsort
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)


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


annotated_profiles_path = pathlib.Path(
    f"{image_base_dir}/8.annotated_profiles/{plate_name}/"
).resolve()
sc_tracks_path = pathlib.Path(
    f"{image_base_dir}/9.single_Cell_tracks_merged/{plate_name}/"
).resolve()
sc_tracks_path.mkdir(exist_ok=True, parents=True)


# In[4]:


list_of_parquets_in_annotated_path = natsort.natsorted(
    list(annotated_profiles_path.glob("*.parquet")), key=lambda x: x.name
)


# In[5]:


# tmp writing of the parquet files to the sc_tracks_path with new names sop pathing works later
for parquet_file in tqdm.tqdm(list_of_parquets_in_annotated_path):
    output_file = (
        sc_tracks_path
        / f'{parquet_file.stem.replace("annotated", "sc_tracks_merged")}.parquet'
    )
    if not output_file.exists():
        shutil.copy(
            parquet_file,
            sc_tracks_path
            / f'{parquet_file.stem.replace("annotated", "sc_tracks_merged")}.parquet',
        )
