#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pathlib
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# In[2]:


WELLS = 40
FOVS = 4
TIMEPOINTS = 288
NUM_MASKS_PER = 2

TOTAL_FILES_EXPECTED = WELLS * FOVS * TIMEPOINTS * NUM_MASKS_PER


# In[3]:


time_counts = {
    "day": ["7/14", "7/14"],
    "time": ["11:20", "11:50"],
    "AM/PM": ["AM", "AM"],
    "files_present": [0, 1.5],
}


# In[4]:


def get_file_count(target_dir):
    return sum(1 for p in target_dir.rglob("*") if p.is_file())


def get_times():
    current_year = time.localtime().tm_year
    current_month = time.localtime().tm_mon
    current_day = time.localtime().tm_mday
    current_hour = time.localtime().tm_hour
    current_minute = time.localtime().tm_min
    return current_year, current_month, current_day, current_hour, current_minute


target_dir = pathlib.Path(
    os.path.expanduser(
        "~/mnt/bandicoot/live_cell_timelapse_pyroptosis_project_data/processed_data/2.cell_segmentation_masks/plate_2"
    )
)

df_save_path = pathlib.Path("../results/tmp_time_tracking_data.parquet").resolve()
if df_save_path.exists():
    old_df = pd.read_parquet(df_save_path)
else:
    old_df = None


# In[5]:


file_count = get_file_count(target_dir)
current_year, current_month, current_day, current_hour, current_minute = get_times()
current_df = pd.DataFrame(
    [
        {
            "year": current_year,
            "month": current_month,
            "day": current_day,
            "hour": current_hour,
            "minute": current_minute,
            "files_present": file_count,
        }
    ]
)


# In[6]:


current_df["total_files"] = TOTAL_FILES_EXPECTED
current_df["files_present_fraction"] = (
    current_df["files_present"] / current_df["total_files"]
)
current_df["time_year"] = 2026

# convert the day/time columns into a datetime format
current_df["datetime"] = pd.to_datetime(
    current_df["year"].astype(str)
    + "/"
    + current_df["month"].astype(str)
    + "/"
    + current_df["day"].astype(str)
    + " "
    + current_df["hour"].astype(str)
    + ":"
    + current_df["minute"].astype(str),
    format="%Y/%m/%d %H:%M",
)
if old_df is not None:
    df = pd.concat([old_df, current_df], ignore_index=True)
else:
    df = current_df
df.to_parquet(df_save_path, index=False)


# In[7]:


df_predicted = df.copy()

# calculate rates
first_time = df["datetime"].iloc[0]
last_time = df["datetime"].iloc[-1]
percentage_complete = np.round(df["files_present_fraction"].iloc[-1] * 100, 2)

first_seg_file_count = df["files_present"].iloc[0]
last_seg_file_count = df["files_present"].iloc[-1]

elapsed_seconds = (last_time - first_time).total_seconds()
rate = (
    last_seg_file_count - first_seg_file_count
) / elapsed_seconds  # files per second
time_estimation_for_total_files = df["total_files"].unique()[0] / rate  # seconds
time_estimation_for_total_files = time_estimation_for_total_files / 3600
if time_estimation_for_total_files > 24:
    time_estimation_for_total_files = time_estimation_for_total_files / 24
    time_unit = "day"
else:
    time_unit = "hour"
time_estimation_for_total_files = np.round(time_estimation_for_total_files, 2)

print(
    f"Time estimation for total files: {time_estimation_for_total_files} {time_unit}s"
)
print(f"Percentage complete: {percentage_complete}%")
