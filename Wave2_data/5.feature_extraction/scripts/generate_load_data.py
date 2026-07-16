#!/usr/bin/env python
# coding: utf-8

# This notebook generates a loaddata file specific for CellProfiler.
# This is needed when the segmentation mask images are in a separate directory from the raw images, and the file names are not exactly the same.
#

# In[1]:


import argparse
import os
import pathlib
import re
import time

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


# In[2]:


if not in_notebook:
    args = argparse.ArgumentParser()
    args.add_argument(
        "--plate_name",
        type=str,
        required=True,
        help="Name of the plate to process (e.g. '2023-08-01_plate1')",
    )
    plate_name = args.parse_args().plate_name
else:
    plate_name = "plate_2"


# In[3]:


if plate_name == "plate_1":
    num_channels = 5
elif plate_name == "plate_2":
    num_channels = 4


# ## Set paths and variables

# In[4]:


if plate_name == "plate_1":

    fieldnames = [
        "Metadata_Well",
        "Metadata_Time",
        "Metadata_WellFOV",
        "Image_FileName_CL640",
        "Image_PathName_CL640",
        "Image_FileName_CL488",
        "Image_PathName_CL488",
        "Image_FileName_SYTOXGreen",
        "Image_PathName_SYTOXGreen",
        "Image_FileName_NucleoLive",
        "Image_PathName_NucleoLive",
        "Image_FileName_BF",
        "Image_PathName_BF",
        "Image_ObjectsFileName_Nuclei",
        "Image_ObjectsPathName_Nuclei",
        "Image_ObjectsFileName_Cells",
        "Image_ObjectsPathName_Cells",
    ]
elif plate_name == "plate_2":
    fieldnames = [
        "Metadata_Well",
        "Metadata_Time",
        "Metadata_WellFOV",
        "Image_FileName_CL640",
        "Image_PathName_CL640",
        "Image_FileName_CL488",
        "Image_PathName_CL488",
        "Image_FileName_SYTOXGreen",
        "Image_PathName_SYTOXGreen",
        "Image_FileName_NucleoLive",
        "Image_PathName_NucleoLive",
        "Image_ObjectsFileName_Nuclei",
        "Image_ObjectsPathName_Nuclei",
        "Image_ObjectsFileName_Cells",
        "Image_ObjectsPathName_Cells",
    ]


# In[5]:


# Define paths and regex patterns
raw_pattern = re.compile(
    r"^(?P<Well>[A-Z]\d+_\d+)_T(?P<Time>\d+)_C(?P<Channel>[1-5])_illumcorrect\.tif{1,2}$"
)
mask_pattern = re.compile(
    r"^(?P<Well>[A-Z]\d+_\d+)_T(?P<Time>\d+)_(?P<MaskChannel>cell|nuclei)_mask\.tif{1,2}$"
)

# Get unique well_fov combinations
base_path = image_based_dir / "processed_data"
raw_dir = base_path / "1.illumination_corrected_files" / plate_name

well_fovs = set()
if raw_dir.exists():
    for well_fov_dir in raw_dir.iterdir():
        if well_fov_dir.is_dir():
            well_fovs.add(well_fov_dir.name)

well_fovs = sorted(list(well_fovs))

all_rows = []
incomplete_records = []
total_incomplete_rows = 0
missing_raw_channel_counts = {str(i): 0 for i in range(1, num_channels + 1)}
missing_mask_counts = {"nuclei": 0, "cell": 0}

# Process each well_fov
for well_fov in tqdm.tqdm(well_fovs):
    raw_image_dir = raw_dir / well_fov
    mask_image_dir = base_path / "2.cell_segmentation_masks" / plate_name / well_fov

    # Organize images by timepoint
    timepoint_data = {}

    # Collect raw images
    if raw_image_dir.exists():
        for img_file in raw_image_dir.iterdir():
            if img_file.is_file():
                match = raw_pattern.match(img_file.name)
                if match:
                    well = match.group("Well")
                    time = int(match.group("Time"))
                    channel = match.group("Channel")

                    if time not in timepoint_data:
                        timepoint_data[time] = {
                            "well": well,
                            "raw_images": {},
                            "masks": {},
                        }
                    timepoint_data[time]["raw_images"][channel] = img_file

    # Collect mask images
    if mask_image_dir.exists():
        for mask_file in mask_image_dir.iterdir():
            if mask_file.is_file():
                match = mask_pattern.match(mask_file.name)
                if match:
                    time = int(match.group("Time"))
                    mask_channel = match.group("MaskChannel")

                    if time in timepoint_data:
                        timepoint_data[time]["masks"][mask_channel] = mask_file

    for time in sorted(timepoint_data.keys()):
        data = timepoint_data[time]

        # Require all n channels + both masks
        missing_raw_channels = [
            str(i)
            for i in range(1, num_channels + 1)
            if str(i) not in data["raw_images"]
        ]
        missing_masks = [
            mask_name
            for mask_name in ("nuclei", "cell")
            if mask_name not in data["masks"]
        ]

        has_all_channels = len(missing_raw_channels) == 0
        has_both_masks = len(missing_masks) == 0

        if not (has_all_channels and has_both_masks):
            total_incomplete_rows += 1

            for channel_name in missing_raw_channels:
                missing_raw_channel_counts[channel_name] += 1
            for mask_name in missing_masks:
                missing_mask_counts[mask_name] += 1

            incomplete_records.append(
                {
                    "Metadata_WellFOV": well_fov,
                    "Metadata_Time": time,
                    "Metadata_Well": data["well"],
                    "missing_raw_channels": ",".join(missing_raw_channels),
                    "missing_masks": ",".join(missing_masks),
                    "reason": "missing_raw"
                    if missing_raw_channels
                    else "missing_masks",
                }
            )
            continue
        if num_channels == 5:
            all_rows.append(
                {
                    "Metadata_Well": data["well"],
                    "Metadata_Time": time,
                    "Metadata_WellFOV": well_fov,
                    "Image_FileName_CL640": data["raw_images"]["1"].name,
                    "Image_PathName_CL640": str(data["raw_images"]["1"].parent),
                    "Image_FileName_CL488": data["raw_images"]["2"].name,
                    "Image_PathName_CL488": str(data["raw_images"]["2"].parent),
                    "Image_FileName_SYTOXGreen": data["raw_images"]["3"].name,
                    "Image_PathName_SYTOXGreen": str(data["raw_images"]["3"].parent),
                    "Image_FileName_NucleoLive": data["raw_images"]["4"].name,
                    "Image_PathName_NucleoLive": str(data["raw_images"]["4"].parent),
                    "Image_FileName_BF": data["raw_images"]["5"].name,
                    "Image_PathName_BF": str(data["raw_images"]["5"].parent),
                    "Image_ObjectsFileName_Nuclei": data["masks"]["nuclei"].name,
                    "Image_ObjectsPathName_Nuclei": str(data["masks"]["nuclei"].parent),
                    "Image_ObjectsFileName_Cells": data["masks"]["cell"].name,
                    "Image_ObjectsPathName_Cells": str(data["masks"]["cell"].parent),
                }
            )
        elif num_channels == 4:
            all_rows.append(
                {
                    "Metadata_Well": data["well"],
                    "Metadata_Time": time,
                    "Metadata_WellFOV": well_fov,
                    "Image_FileName_CL640": data["raw_images"]["1"].name,
                    "Image_PathName_CL640": str(data["raw_images"]["1"].parent),
                    "Image_FileName_CL488": data["raw_images"]["2"].name,
                    "Image_PathName_CL488": str(data["raw_images"]["2"].parent),
                    "Image_FileName_SYTOXGreen": data["raw_images"]["3"].name,
                    "Image_PathName_SYTOXGreen": str(data["raw_images"]["3"].parent),
                    "Image_FileName_NucleoLive": data["raw_images"]["4"].name,
                    "Image_PathName_NucleoLive": str(data["raw_images"]["4"].parent),
                    "Image_ObjectsFileName_Nuclei": data["masks"]["nuclei"].name,
                    "Image_ObjectsPathName_Nuclei": str(data["masks"]["nuclei"].parent),
                    "Image_ObjectsFileName_Cells": data["masks"]["cell"].name,
                    "Image_ObjectsPathName_Cells": str(data["masks"]["cell"].parent),
                }
            )

# Create a single DataFrame containing all complete rows
load_df = pd.DataFrame(all_rows, columns=fieldnames)

# Write one CSV per (well_fov, timepoint) with a single row each
for (well_fov, time), group_df in load_df.groupby(
    ["Metadata_WellFOV", "Metadata_Time"]
):
    load_data_path = pathlib.Path(
        f"{root_dir}/Wave2_data/5.feature_extraction/loadfiles/{plate_name}/{well_fov}_T{int(time):04d}/load_file.csv"
    )
    load_data_path.parent.mkdir(parents=True, exist_ok=True)
    group_df.to_csv(load_data_path, index=False)

# Build diagnostic summaries
incomplete_df = pd.DataFrame(incomplete_records)
reason_summary = (
    incomplete_df["reason"]
    .value_counts()
    .rename_axis("reason")
    .reset_index(name="count")
    if not incomplete_df.empty
    else pd.DataFrame(columns=["reason", "count"])
)
missing_raw_summary_df = pd.DataFrame(
    [
        {"raw_channel": f"C{channel}", "missing_count": count}
        for channel, count in missing_raw_channel_counts.items()
    ]
).sort_values("missing_count", ascending=False)
missing_mask_summary_df = pd.DataFrame(
    [
        {"mask": mask_name, "missing_count": count}
        for mask_name, count in missing_mask_counts.items()
    ]
).sort_values("missing_count", ascending=False)

print(
    f"\nAll per-timepoint load files generated successfully! Rows written: {len(load_df)}"
)
print(f"Incomplete rows skipped: {total_incomplete_rows}")

print("\nSkip reason summary:")
print(reason_summary.to_string(index=False))

print("\nMissing raw channel counts:")
print(missing_raw_summary_df.to_string(index=False))

print("\nMissing mask counts:")
print(missing_mask_summary_df.to_string(index=False))

if not incomplete_df.empty:
    print("\nExample incomplete well_fov/timepoints:")
    print(
        incomplete_df[
            [
                "Metadata_WellFOV",
                "Metadata_Time",
                "Metadata_Well",
                "missing_raw_channels",
                "missing_masks",
                "reason",
            ]
        ]
        .head(15)
        .to_string(index=False)
    )
