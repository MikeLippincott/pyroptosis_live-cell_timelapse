#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import os
import pathlib

import matplotlib.pyplot as plt
import natsort
import numpy as np
import pandas as pd
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm


# ## Set paths and variables

# In[2]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(
    f"{image_base_dir}/live_cell_timelapse_pyroptosis_project_data/processed_data/"
).resolve(strict=True)
converted_profiles_dir = pathlib.Path(
    f"{image_base_dir}/4.converted_profiles/"
).resolve(strict=True)

combined_profiles_path = pathlib.Path(
    f"{image_base_dir}/5.combined_profiles/"
).resolve()
combined_profiles_path.mkdir(exist_ok=True)


# In[3]:


# well_fov_timepoints - get all the well_fov_timepoints that we have extracted features for
converted_profiles = [
    x for x in tqdm.tqdm(converted_profiles_dir.glob("*")) if x.is_dir()
]
# sort the converted profiles in natural order
converted_profiles = natsort.natsorted(converted_profiles)
# get all the converted profile parquet files as a list of paths to use downstream
converted_profiles = [
    list(x.glob("**/*.parquet"))[0]
    for x in tqdm.tqdm(converted_profiles)
    if len(list(x.glob("**/*.parquet"))) > 0
]
converted_profiles = natsort.natsorted(converted_profiles)
print(f"Number of converted profiles: {len(converted_profiles)}")


# In[4]:


# get a list of all files in the data directory
df = pd.concat([pd.read_parquet(file) for file in converted_profiles])
df.reset_index(inplace=True, drop=True)
print(df.shape)
df.to_parquet(combined_profiles_path / "combined_profiles.parquet")
df.head()
