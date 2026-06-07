#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import pathlib

import matplotlib.pyplot as plt
import natsort
import pandas as pd
import seaborn as sns
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
ic_image_dir = pathlib.Path(
    f"{image_base_dir}/1.illumination_corrected_files/"
).resolve(strict=True)

load_data_file_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/load_data/load_file.txt"
).resolve()
load_data_file_path.parent.mkdir(exist_ok=True, parents=True)


# In[3]:


# well_fov_timepoints
image_list = [x for x in tqdm.tqdm(ic_image_dir.glob("*")) if x.is_dir()]
image_list = natsort.natsorted(image_list)
image_list = [
    list(x.glob("**/*.tiff"))
    for x in tqdm.tqdm(image_list)
    if len(list(x.glob("**/*.tiff"))) > 0
]
image_list = natsort.natsorted(image_list)
print(f"Number of images: {len(image_list)}")


# In[4]:


# unnest the nested list of lists
new_image_list = [
    item
    for image_list_item in image_list
    for item in image_list_item
    if isinstance(image_list_item, list) and isinstance(item, pathlib.Path)
]
print(f"Number of images after unnesting: {len(new_image_list)}")


# In[ ]:


# create a dataframe with the image paths and extract the well_fov_time from the file names
# extract the well_fov_time from the file names and save to a text file for loading in the next notebook
df = pd.DataFrame({"image_path": new_image_list})
df["file_name"] = df["image_path"].apply(lambda x: x.stem)
df["well_fov_time"] = df["file_name"].apply(lambda x: "_".join(x.split("_")[:3]))
df["well_fov_time"] = df["well_fov_time"].str.replace("T", "")
well_fov_times = natsort.natsorted(list(set(df["well_fov_time"].to_list())))

with open(load_data_file_path, "w") as f:
    for item in well_fov_times:
        f.write(f"{item}\n")
print(
    f"Saved load data file with {len(well_fov_times)} entries to {load_data_file_path}"
)
