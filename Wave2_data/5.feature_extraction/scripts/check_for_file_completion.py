#!/usr/bin/env python
# coding: utf-8

# This notebook generates the well, FOV, timepoint image-sets that still need to be run.
# Generating this loadfile of sorts cuts down on computation time by not running the same image-sets multiple times.
# This is a super archaeic form of preemptive caching, but it works.

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
image_based_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_based_dir = (
    image_based_dir / "live_cell_timelapse_pyroptosis_project_data/processed_data"
)


# In[2]:


# get a list of the well_fov directories for each patient
well_fov_dirs = [
    x
    for x in pathlib.Path(f"{image_based_dir}/1.illumination_corrected_files").iterdir()
    if x.is_dir()
]
# get timepoints per well_fov
well_fov_timepoint_raw_file_paths = []
for well_fov_dir in tqdm.tqdm(well_fov_dirs):
    timepoint_dirs = sorted(well_fov_dir.glob(f"*/"))
    for timepoint_dir in timepoint_dirs:
        well_fov_timepoint_raw_file_paths.append(timepoint_dir)
well_fov_df = pd.DataFrame(
    {
        "well_fov_timepoint": [x for x in well_fov_timepoint_raw_file_paths],
    }
)
well_fov_df["well_fov"] = well_fov_df["well_fov_timepoint"].apply(
    lambda x: "_".join(x.name.split("_")[:2])
)
well_fov_df["timepoint"] = well_fov_df["well_fov_timepoint"].apply(
    lambda x: x.name.split("_")[2]
)
# keep T prefix and pad only the numeric part to 4 digits (e.g., T9 -> T0009)
well_fov_df["timepoint"] = well_fov_df["timepoint"].apply(
    lambda x: f"T{str(x)[1:].zfill(4)}"
    if str(x).startswith("T")
    else f"T{str(x).zfill(4)}"
)
well_fov_df.drop_duplicates(subset=["well_fov", "timepoint"], inplace=True)


# In[3]:


# Build expected output sqlite path per well_fov + timepoint row
well_fov_df["output_path"] = well_fov_df["well_fov_timepoint"].apply(
    lambda x: str(pathlib.Path(x).parents[2] / "3.extracted_features")
)

well_fov_df["output_file_path"] = [
    str(
        pathlib.Path(output_path)
        / f"{well_fov}_{timepoint}"
        / f"{well_fov}_{timepoint}.sqlite"
    )
    for output_path, well_fov, timepoint in zip(
        well_fov_df["output_path"],
        well_fov_df["well_fov"],
        well_fov_df["timepoint"],
    )
]

well_fov_df["output_file_path_exists"] = well_fov_df["output_file_path"].apply(
    lambda x: pathlib.Path(x).exists()
)


# In[4]:


# sort the df
well_fov_df.sort_values(by=["well_fov", "timepoint"], inplace=True)
# natural sort the df by well_fov and timepoint
well_fov_df = well_fov_df.iloc[
    natsort.index_natsorted(
        well_fov_df["well_fov"].astype(str) + "_" + well_fov_df["timepoint"].astype(str)
    )
].reset_index(drop=True)
well_fov_df.head()


# In[5]:


# find the number of well fov timepoints still needed
to_run = well_fov_df.loc[well_fov_df["output_file_path_exists"] == False]
completed = well_fov_df.loc[well_fov_df["output_file_path_exists"] == True]
print(f"Number of well fov timepoints still needed: {len(to_run)}")
print(f"Number of well fov timepoints completed: {len(completed)}")
print(f"Progress: {len(completed) / len(well_fov_df) * 100:.2f}%")
