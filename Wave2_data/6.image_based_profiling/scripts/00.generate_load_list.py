#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pathlib

import natsort
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


# In[4]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
image_dir = pathlib.Path(f"{image_base_dir}/0.renamed_files/{plate_name}").resolve(
    strict=True
)

load_data_well_fov_time_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/load_data/load_file_well_fov_time.txt"
).resolve()
load_data_well_fov_path = pathlib.Path(
    f"{root_dir}/Wave2_data/6.image_based_profiling/load_data/load_file_well_fov.txt"
).resolve()
load_data_well_fov_time_path.parent.mkdir(exist_ok=True, parents=True)


# In[5]:


# well_fov_timepoints
image_list = [x for x in tqdm.tqdm(image_dir.glob("*")) if x.is_dir()]
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


# In[5]:


# create a dataframe with the image paths and extract the well_fov_time from the file names
# extract the well_fov_time from the file names and save to a text file for loading in the next notebook
df = pd.DataFrame({"image_path": new_image_list})
df["file_name"] = df["image_path"].apply(lambda x: x.stem)
df["well_fov_time"] = df["file_name"].apply(lambda x: "_".join(x.split("_")[:3]))
df["well_fov_time"] = df["well_fov_time"].str.replace("T", "")
df["time"] = df["well_fov_time"].apply(lambda x: f"T{x.split('_')[-1].zfill(4)}")
# add time back to the well_fov_time
df["well_fov_time"] = df["well_fov_time"].apply(lambda x: "_".join(x.split("_")[:2]))
df["well_fov_time"] = df["well_fov_time"] + "_" + df["time"]
well_fov_times = natsort.natsorted(list(set(df["well_fov_time"].to_list())))
well_fovs = natsort.natsorted(
    list(set(df["well_fov_time"].apply(lambda x: "_".join(x.split("_")[:2])).to_list()))
)
print(f"Number of unique well_fov_time: {len(well_fov_times)}")
print(f"Number of unique well_fov: {len(well_fovs)}")


# In[6]:


with open(load_data_well_fov_time_path, "w") as f:
    for item in well_fov_times:
        f.write(f"{item}\n")
print(
    f"Saved load data file with {len(well_fov_times)} entries to {load_data_well_fov_time_path}"
)


with open(load_data_well_fov_path, "w") as f:
    for item in well_fovs:
        f.write(f"{item}\n")
print(
    f"Saved load data file with {len(well_fovs)} entries to {load_data_well_fov_path}"
)
