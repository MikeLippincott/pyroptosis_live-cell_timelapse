#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib

import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import skimage
import tifffile
import tqdm

# In[2]:


def create_composite_image(
    lut_dict: dict, image_path_list: list, num_channels: int = 3
) -> np.ndarray:
    """
    Create a composite image from three grayscale images using a lookup table.

    Parameters
    ----------
    lut_dict : dict
        Dictionary containing the lookup tables for the three images.
    image_path_list : list
        List of three image paths.

    Returns
    -------
    np.ndarray
        Composite image.
    """
    assert (
        len(image_path_list) == num_channels
    ), "Number of images must be equal to the number of channels. There are {} images and {} channels.".format(
        len(image_path_list), num_channels
    )
    if num_channels == 3:
        image1 = cv2.imread(str(image_path_list[0]), cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(str(image_path_list[1]), cv2.IMREAD_GRAYSCALE)
        image3 = cv2.imread(str(image_path_list[2]), cv2.IMREAD_GRAYSCALE)

        # bgr
        image1 = cv2.merge([image1, image1, image1])
        image2 = cv2.merge([image2, image2, image2])
        image3 = cv2.merge([image3, image3, image3])
        # Apply the colormap lookup table to the grayscale image
        image1 = cv2.LUT(image1, lut_dict["2"])
        image2 = cv2.LUT(image2, lut_dict["3"])
        image3 = cv2.LUT(image3, lut_dict["4"])
        # adjust contrast
        image1 = cv2.convertScaleAbs(image1, alpha=10)
        image2 = cv2.convertScaleAbs(image2, alpha=20)
        image3 = cv2.convertScaleAbs(image3, alpha=15)

        composite_image = cv2.addWeighted(image1, 1, image2, 1, 0)
        composite_image = cv2.addWeighted(composite_image, 1, image3, 1, 0)
    if num_channels == 4:
        image1 = cv2.imread(str(image_path_list[0]), cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(str(image_path_list[1]), cv2.IMREAD_GRAYSCALE)
        image3 = cv2.imread(str(image_path_list[2]), cv2.IMREAD_GRAYSCALE)
        image4 = cv2.imread(str(image_path_list[3]), cv2.IMREAD_GRAYSCALE)

        # bgr
        image1 = cv2.merge([image1, image1, image1])
        image2 = cv2.merge([image2, image2, image2])
        image3 = cv2.merge([image3, image3, image3])
        image4 = cv2.merge([image4, image4, image4])
        # Apply the colormap lookup table to the grayscale image
        image1 = cv2.LUT(image1, lut_dict["1"])
        image2 = cv2.LUT(image2, lut_dict["2"])
        image3 = cv2.LUT(image3, lut_dict["3"])
        image4 = cv2.LUT(image4, lut_dict["4"])
        # adjust contrast
        image1 = cv2.convertScaleAbs(image1, alpha=10)
        image2 = cv2.convertScaleAbs(image2, alpha=20)
        image3 = cv2.convertScaleAbs(image3, alpha=15)
        image4 = cv2.convertScaleAbs(image4, alpha=15)

        composite_image = cv2.addWeighted(image1, 1, image2, 1, 0)
        composite_image = cv2.addWeighted(composite_image, 1, image3, 1, 0)
        composite_image = cv2.addWeighted(composite_image, 1, image4, 1, 0)
    return composite_image


# In[3]:


def make_animation_gif(
    image_list: int,
    save_path: pathlib.Path,
    duration: int = 500,
    fps: int = 5,
    loop: int = 0,
):

    imageio.mimsave(save_path, image_list, duration=duration, loop=loop, fps=fps)


# ### Define the LUTs

# In[4]:


# Create a lookup table (256 values, mapping grayscale to magenta)
magenta_lut = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    magenta_lut[i] = [i, 0, i]  # R = i, G = 0, B = i (magenta gradient)
# Create a lookup table (256 values, mapping grayscale to yellow)
yellow_lut = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    yellow_lut[i] = [i, i, 0]  # R = i, G = i, B = 0 (yellow gradient)
# Create a lookup table (256 values, mapping grayscale to cyan)
cyan_lut = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    cyan_lut[i] = [0, i, i]  # R = 0, G = i, B = i (cyan gradient)
# Create a lookup table (256 values, mapping grayscale to green)
green_lut = np.zeros((256, 1, 3), dtype=np.uint8)
for i in range(256):
    green_lut[i] = [0, i, 0]  # R = 0, G = i, B = 0 (green gradient)
lut_dict = {"1": green_lut, "2": magenta_lut, "3": yellow_lut, "4": cyan_lut}


# In[5]:


# path the the data
image_data_path = pathlib.Path("../../../data/raw").resolve(strict=True)
image_gifs_path = pathlib.Path("../figures/image_gifs/").resolve()
image_gifs_path.mkdir(parents=True, exist_ok=True)


# In[6]:


# get all dirs in the path
all_dirs = [x for x in image_data_path.iterdir() if x.is_dir()]
all_dirs = sorted(all_dirs)


# In[7]:


channels_to_plot = ["2", "3", "4"]


# In[8]:


# loop through each well_fov_dir
all_dfs = []
for well_fov_dir in all_dirs:
    # get all files in the first dir
    all_files = [x for x in well_fov_dir.iterdir() if x.is_file()]
    all_files = sorted(all_files)
    all_files = [x for x in all_files if not "mask" in x.stem]
    # make a df out of the files in the first dir
    df = pd.DataFrame(all_files, columns=["file_path"])
    df["file_name"] = (
        df["file_path"].apply(lambda x: x.stem).str.split("_illumcorrect").str[0]
    )
    df["time"] = df["file_name"].str.split("_").str[0]
    df["well_fov"] = df["file_name"].str.split("_W").str[1].str.split("_C").str[0]
    df["channel"] = df["file_name"].str.split("_C").str[1]
    # drop the max timepoint
    df = df[df["time"] != df["time"].max()]
    df = df[df["channel"].isin(channels_to_plot)]
    all_dfs.append(df)
df = pd.concat(all_dfs)
# sort by well_fov and time
df = df.sort_values(by=["well_fov", "time"])
df.head()


# In[9]:


overwrite = False
# loop through each well_fov and make a gif
for well_fov in tqdm.tqdm(df["well_fov"].unique()):
    tmp_well_df = df[df["well_fov"] == well_fov]
    list_of_images = []
    save_path = pathlib.Path(image_gifs_path / f"{well_fov}_CL448-561_DNA.gif")
    if save_path.exists() and overwrite is False:
        pass
    elif save_path.exists() and overwrite is True:
        for time in df["time"].unique():
            tmp_time_df = tmp_well_df[tmp_well_df["time"] == time]
            list_of_images.append(
                create_composite_image(
                    lut_dict,
                    tmp_time_df["file_path"].tolist(),
                    num_channels=len(channels_to_plot),
                )
            )
        make_animation_gif(
            image_list=list_of_images, save_path=save_path, duration=1000, fps=2, loop=0
        )


# ## Add in GSDM

# In[10]:


channels_to_plot = ["1", "2", "3", "4"]


# In[11]:


# loop through each well_fov_dir
all_dfs = []
for well_fov_dir in all_dirs:
    # get all files in the first dir
    all_files = [x for x in well_fov_dir.iterdir() if x.is_file()]
    all_files = sorted(all_files)
    all_files = [x for x in all_files if not "mask" in x.stem]
    # make a df out of the files in the first dir
    df = pd.DataFrame(all_files, columns=["file_path"])
    df["file_name"] = (
        df["file_path"].apply(lambda x: x.stem).str.split("_illumcorrect").str[0]
    )
    df["time"] = df["file_name"].str.split("_").str[0]
    df["well_fov"] = df["file_name"].str.split("_W").str[1].str.split("_C").str[0]
    df["channel"] = df["file_name"].str.split("_C").str[1]
    # drop the max timepoint
    df = df[df["time"] != df["time"].max()]
    df = df[df["channel"].isin(channels_to_plot)]
    all_dfs.append(df)
df = pd.concat(all_dfs)
# sort by well_fov and time
df = df.sort_values(by=["well_fov", "time"])
df.head()


# In[12]:


# loop through each well_fov and make a gif
for well_fov in tqdm.tqdm(df["well_fov"].unique()):
    tmp_well_df = df[df["well_fov"] == well_fov]
    save_path = pathlib.Path(image_gifs_path / f"{well_fov}_GSDM_CL488-561_DNA.gif")
    list_of_images = []
    if save_path.exists() and overwrite is False:
        pass

    elif not save_path.exists() or overwrite is True:
        for time in tmp_well_df["time"].unique():
            tmp_time_df = tmp_well_df[tmp_well_df["time"] == time]
            list_of_images.append(
                create_composite_image(
                    lut_dict,
                    tmp_time_df["file_path"].tolist(),
                    num_channels=len(channels_to_plot),
                )
            )
        make_animation_gif(
            image_list=list_of_images, save_path=save_path, duration=1000, fps=2, loop=0
        )
