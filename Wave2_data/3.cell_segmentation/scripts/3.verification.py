#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import os
import pathlib

import matplotlib.pyplot as plt
import natsort

# Import dependencies
import numpy as np
import pandas as pd
import skimage
import tifffile
import torch
from cellpose import models
from csbdeep.utils import normalize
from PIL import Image
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm


# In[2]:


if not in_notebook:
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to process",
    )
    args = parser.parse_args()
    plate_name = args.plate_name


else:
    plate_name = "plate_2"


image_base_dir = bandicoot_check(
    root_dir=root_dir,
    bandicoot_mount_path=pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(),
)


segmentation_mask_output_dir = pathlib.Path(
    image_base_dir / "processed_data" / "2.cell_segmentation_masks" / plate_name
).resolve()


# ## Set up images, paths and functions

# In[3]:


well_fovs = segmentation_mask_output_dir.glob("*")
well_fovs = [d for d in well_fovs if d.is_dir()]
files = list(
    [[f for f in dir.glob("*nuclei_mask.tif*") if f.is_file()] for dir in well_fovs]
)
files = [f for sublist in files for f in sublist]


# In[4]:


df = pd.DataFrame({"nuclei_mask_file_path": files})
df["cell_mask_file_path"] = df["nuclei_mask_file_path"].apply(
    lambda x: str(x).replace("nuclei_mask", "cell_mask")
)
df.insert(
    0, "well_fov", df["nuclei_mask_file_path"].apply(lambda x: str(x).split("/")[-2])
)
df.insert(
    1,
    "nuclei_mask_present",
    df["nuclei_mask_file_path"].apply(lambda x: pathlib.Path(x).is_file()),
)
df.insert(
    2,
    "cell_mask_present",
    df["cell_mask_file_path"].apply(lambda x: pathlib.Path(x).is_file()),
)
df["both_masks_present"] = df["nuclei_mask_present"] & df["cell_mask_present"]
# read the masks in and verify that the object labels match between the two masks
# df['mask_ids_match'] = None
# for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0], desc="Verifying masks"):
#     try:
#         nuclei_mask = tifffile.imread(row['nuclei_mask_file_path'])
#         cell_mask = tifffile.imread(row['cell_mask_file_path'])
#         if np.max(nuclei_mask) != np.max(cell_mask):
#             df.at[index, 'both_masks_present'] = False
#         else:
#             df.at[index, 'mask_ids_match'] = True
#     except Exception as e:
#         print(f"Error reading masks for {row['well_fov']}: {e}")


# In[5]:


# filter the dataframe for rows where both masks are not present and the mask ids do not  match
# rerun_df = df[~df['both_masks_present'] or ~df['mask_ids_match']]
rerun_df = df[~df["both_masks_present"]]
print(f"Found {rerun_df.shape[0]} well fov timepoints that need to be rerun.")
rerun_df
