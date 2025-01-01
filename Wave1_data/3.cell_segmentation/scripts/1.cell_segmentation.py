#!/usr/bin/env python
# coding: utf-8

# This notebook focuses on trying to find a way to segment cells within organoids properly.
# The end goals is to segment cell and extract morphology features from cellprofiler.
# These masks must be imported into cellprofiler to extract features.

# In[ ]:


import argparse
import pathlib

import matplotlib.pyplot as plt

# Import dependencies
import numpy as np
import skimage
import tifffile

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False

print(in_notebook)


# In[ ]:


if not in_notebook:
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--input_dir",
        type=str,
        help="Path to the input directory containing the tiff images",
    )

    args = parser.parse_args()
    clip_limit = args.clip_limit
    input_dir = pathlib.Path(args.input_dir).resolve(strict=True)

else:
    input_dir = pathlib.Path(
        "../../2.illumination_correction/illum_directory/W0052_F0001"
    ).resolve(strict=True)


# ## Set up images, paths and functions

# In[ ]:


image_extensions = {".tif", ".tiff"}
files = sorted(input_dir.glob("*"))
files = [str(x) for x in files if x.suffix in image_extensions]


# In[ ]:


image_dict = {
    "nuclei_file_paths": [],
    "nuclei": [],
    "cytoplasm1": [],
    "cytoplasm2": [],
}


# In[ ]:


# split files by channel
for file in files:
    if "C4" in file.split("/")[-1]:
        image_dict["nuclei_file_paths"].append(file)
        image_dict["nuclei"].append(tifffile.imread(file).astype(np.float32))
    elif "C2" in file.split("/")[-1]:
        image_dict["cytoplasm1"].append(tifffile.imread(file).astype(np.float32))
    elif "C3" in file.split("/")[-1]:
        image_dict["cytoplasm2"].append(tifffile.imread(file).astype(np.float32))

cytoplasm_image_list = [
    np.max(np.array([cytoplasm1, cytoplasm2]), axis=0)
    for cytoplasm1, cytoplasm2 in zip(
        image_dict["cytoplasm1"], image_dict["cytoplasm2"]
    )
]
nuclei_image_list = [np.array(nuclei) for nuclei in image_dict["nuclei"]]

cyto = np.array(cytoplasm_image_list).astype(np.int32)
nuclei = np.array(nuclei_image_list).astype(np.int32)

cyto = skimage.exposure.equalize_adapthist(cyto, clip_limit=clip_limit + 0.5)
nuclei = skimage.exposure.equalize_adapthist(nuclei, clip_limit=clip_limit)


print(cyto.shape, nuclei.shape)


# In[ ]:


original_nuclei_image = nuclei.copy()
original_cyto_image = cyto.copy()


# In[ ]:


if in_notebook:
    # plot the nuclei and the cyto channels
    plt.figure(figsize=(10, 10))
    plt.subplot(121)
    plt.imshow(nuclei[1, :, :], cmap="gray")
    plt.title("nuclei")
    plt.axis("off")
    plt.subplot(122)
    plt.imshow(cyto[1, :, :], cmap="gray")
    plt.title("cyto")
    plt.axis("off")
    plt.show()


# In[ ]:


imgs = []
# save each z-slice as an RGB png
for z in range(nuclei.shape[0]):

    nuclei_tmp = nuclei[z, :, :]
    cyto_tmp = cyto[z, :, :]
    nuclei_tmp = (nuclei_tmp / nuclei_tmp.max() * 255).astype(np.uint8)
    cyto_tmp = (cyto_tmp / cyto_tmp.max() * 255).astype(np.uint8)
    # save the image as an RGB png with nuclei in blue and cytoplasm in red
    RGB = np.stack([cyto_tmp, np.zeros_like(cyto_tmp), nuclei_tmp], axis=-1)

    # change to 8-bit
    RGB = (RGB / RGB.max() * 255).astype(np.uint8)

    rgb_image_pil = Image.fromarray(RGB)

    imgs.append(rgb_image_pil)


# ## Cellpose

# In[ ]:


# model_type='cyto' or 'nuclei' or 'cyto2' or 'cyto3'
model_name = "cyto3"
model = models.Cellpose(model_type=model_name, gpu=use_GPU)

channels = [[1, 3]]  # channels=[red cells, blue nuclei]
diameter = 30

masks_all_dict = {"masks": [], "imgs": []}
imgs = np.array(imgs)

# get masks for all the images
# save to a dict for later use
for img in imgs:
    # masks, flows, styles, diams = model.eval(img, diameter=diameter, channels=channels)
    masks, flows, styles, diams = model.eval(img, channels=channels)

    masks_all_dict["masks"].append(masks)
    masks_all_dict["imgs"].append(img)
print(len(masks_all_dict))
masks_all = masks_all_dict["masks"]
imgs = masks_all_dict["imgs"]


# In[ ]:


if in_notebook:
    # masks, flows, styles, diams
    # plt.title(f"z: {z}")
    for z in range(len(masks_all)):
        plt.figure(figsize=(30, 10))
        plt.subplot(1, 4, 1)
        plt.imshow(nuclei[z], cmap="gray")
        plt.title("Nuclei")
        plt.axis("off")

        plt.subplot(142)
        plt.imshow(cyto[z], cmap="gray")
        plt.title("Cytoplasm")
        plt.axis("off")

        plt.subplot(143)
        plt.imshow(imgs[z], cmap="gray")
        plt.title("Red: Cytoplasm, Blue: Nuclei")
        plt.axis("off")

        plt.subplot(144)
        plt.imshow(masks_all[z], cmap="gray")
        plt.title("Cell masks")
        plt.axis("off")
        plt.show()


# In[ ]:


for frame_index, frame in enumerate(image_dict["nuclei_file_paths"]):
    frame
    tifffile.imwrite(
        f"{input_dir}/{str(frame).split('/')[-1].split('_C4')[0]}_cell_mask.tiff",
        nuclei[frame_index, :, :],
    )
