#!/usr/bin/env python
# coding: utf-8

# This is a place holder for merging single-cell tracks with the profiles

# In[10]:


import os
import pathlib
import shutil

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


annotated_profiles_path = pathlib.Path(
    f"{image_base_dir}/8.annotated_profiles/annotated_profiles.parquet"
).resolve()
annotated_profiles_path.parent.mkdir(exist_ok=True)
sc_tracks_path = pathlib.Path(
    f"{image_base_dir}/9.single_Cell_tracks_merged/{plate_name}/sc_tracks_profiles.parquet"
).resolve()


# In[13]:


# copy annotated profiles to sc_tracks_path location as placeholder until we have merged tracks
sc_tracks_path.parent.mkdir(exist_ok=True)
shutil.copy(annotated_profiles_path, sc_tracks_path)
