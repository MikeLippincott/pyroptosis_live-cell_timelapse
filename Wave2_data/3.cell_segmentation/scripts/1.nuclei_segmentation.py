#!/usr/bin/env python
# coding: utf-8

# This notebook focuses on trying to find a way to segment nuclei properly.
# The end goals is to segment cell and extract morphology features from cellprofiler.
# These masks must be imported into cellprofiler to extract features.

# In[1]:


import argparse
import os
import pathlib

import matplotlib.pyplot as plt
import natsort

# Import dependencies
import numpy as np
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
        "--well_fov",
        type=str,
        help="Name of the well and field of view to segment, e.g. B2_1",
    )

    parser.add_argument(
        "--clip_limit",
        type=float,
        help="Clip limit for the adaptive histogram equalization",
    )
    parser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to process",
    )

    args = parser.parse_args()
    clip_limit = args.clip_limit
    well_fov = args.well_fov
    plate_name = args.plate_name


else:
    well_fov = "B2_1"
    clip_limit = 0.6
    plate_name = "plate_2"


image_base_dir = bandicoot_check(
    root_dir=root_dir,
    bandicoot_mount_path=pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(),
)

input_dir = pathlib.Path(
    image_base_dir
    / "processed_data"
    / "1.illumination_corrected_files"
    / plate_name
    / well_fov
).resolve(strict=True)

segmentation_mask_output_dir = pathlib.Path(
    image_base_dir
    / "processed_data"
    / "2.cell_segmentation_masks"
    / plate_name
    / well_fov
).resolve()
segmentation_mask_output_dir.mkdir(exist_ok=True, parents=True)


figures_dir = pathlib.Path("../figures").resolve()
figures_dir.mkdir(exist_ok=True, parents=True)


# ## Set up images, paths and functions

# In[3]:


image_extensions = {".tif", ".tiff"}
files = sorted(input_dir.glob("*"))
files = [str(x) for x in files if x.suffix in image_extensions]
files = natsort.natsorted(files)
files = [x for x in files if "_C4" in x]


# ## Cellpose

# ### Runnning segmentation

# In[4]:


use_GPU = torch.cuda.is_available()
model = models.CellposeModel(
    gpu=use_GPU,
)
masks_all_dict = {"masks": [], "imgs": []}

# get masks for all the images
# save to a dict for later use
for frame, img in tqdm.tqdm(
    enumerate(files), desc="Segmenting nuclei", total=len(files)
):
    save_file_path = (
        f"{segmentation_mask_output_dir}/{well_fov}_T{frame+1}_nuclei_mask.tiff"
    )
    if pathlib.Path(save_file_path).exists():
        continue
    img = tifffile.imread(img)
    img = skimage.exposure.equalize_adapthist(img, clip_limit=clip_limit)
    img = normalize(img)
    masks, flows, styles = model.eval(img)
    tifffile.imwrite(save_file_path, masks)
    if in_notebook:

        masks_all_dict["masks"].append(masks)
        masks_all_dict["imgs"].append(img)


# In[5]:


if in_notebook:
    if len(masks_all_dict["masks"]) > 0:
        masks_all_dict["masks"] = np.array(masks_all_dict["masks"])
        masks_all_dict["imgs"] = np.array(masks_all_dict["imgs"])
        # show the first 5 and the last 5 masks
        for t in [0, 1, 2, 3, 4, -5, -4, -3, -2, -1]:
            plt.figure(figsize=(20, 10))

            plt.title(f"z: {t}")
            plt.axis("off")
            plt.subplot(1, 2, 1)
            plt.imshow(masks_all_dict["imgs"][t], cmap="inferno")
            plt.title("Nuclei")
            plt.axis("off")

            plt.subplot(122)
            plt.imshow(masks_all_dict["masks"][t], cmap="nipy_spectral")
            plt.title("Cell masks")
            plt.axis("off")
            plt.show()
