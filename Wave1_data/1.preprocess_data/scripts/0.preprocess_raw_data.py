#!/usr/bin/env python
# coding: utf-8

# This notebook pre-processes the data to be available in the repo path.

# In[1]:


import glob
import json
import pathlib
import shutil
import string

import pandas as pd
import tqdm

# ## Paths and import data

# In[2]:


# absolute path to the raw data directory (only works on this machine)
path_to_raw_data = pathlib.Path(
    "/home/lippincm/Desktop/18TB/Saguaro_pyroptosis_wave1/"
).resolve(strict=True)

# repository data directory to access the data faster
path_to_repo_data = pathlib.Path("../../../data/raw/").resolve()
path_to_repo_data.mkdir(exist_ok=True, parents=True)

# recurse through the directory and find all the .tif or .tiff files
list_of_files = glob.glob(str(path_to_raw_data / "**/Image/*.tif*"), recursive=True)
print(f"Found {len(list_of_files)} files")


# In[3]:


# copy the files to the repository data directory
for file in tqdm.tqdm(list_of_files):
    file_path = pathlib.Path(file)
    file_parent = file_path.parent
    file_parent_path = path_to_repo_data / pathlib.Path(
        str(file_parent).split("/")[-2]
        / pathlib.Path(str(file_path.stem).split("T")[0].replace("F", "_F"))
    )
    file_parent_path.mkdir(exist_ok=True, parents=True)
    new_file_path = file_parent_path / file_path.name
    if not new_file_path.exists():
        # copy the file to the repository data directory
        shutil.copy(file_path, new_file_path)


# In[4]:


# verify that the number of images in are the same as the number of files copied
list_of_new_files = glob.glob(str(path_to_repo_data / "**/*.tif*"), recursive=True)
print(f"There were {len(list_of_files)} original files")
print(f"We copied {len(list_of_new_files)} files")
assert len(list_of_files) == len(list_of_new_files)


# ## Set up a metadata frame

# In[5]:


# make a df out of the file names
df = pd.DataFrame(list_of_new_files, columns=["file_path"])
df.insert(0, "file_name", df["file_path"].apply(lambda x: pathlib.Path(x).name))
df.insert(0, "Plate", df["file_path"].apply(lambda x: x.split("/")[7]))
df.insert(0, "Well", df["file_name"].apply(lambda x: x.split("F")[0].split("W")[-1]))
df.insert(0, "FOV", df["file_name"].apply(lambda x: x.split("T")[0].split("F")[-1]))
df.drop("file_path", axis=1, inplace=True)
df.drop("file_name", axis=1, inplace=True)
# split the plate into time and date
df.insert(2, "Date_Time", df["Plate"].apply(lambda x: x.strip("_").replace("T", "")))
# format the time into YYYY-MM-DD HH:MM:SS
df["Date_Time"] = pd.to_datetime(df["Date_Time"], format="%Y%m%d%H%M%S")

# sort by Date, Time, Plate, Well, FOV
df.sort_values(by=["Date_Time", "Plate", "Well", "FOV"], inplace=True)
df.reset_index(drop=True, inplace=True)
df.head()


# In[6]:


# well dictionary for mapping
# Generate the dictionary dynamically
# implemented via Jenna Tomkinson
well_map = {
    f"{i:04d}": f"{row}{col:02d}"
    for i, (row, col) in enumerate(
        ((r, c) for r in string.ascii_uppercase[:16] for c in range(1, 25)), start=1
    )
}

# write the well map to a json file
path_to_repo_data = pathlib.Path("../../../data/processed/").resolve()
path_to_repo_data.mkdir(exist_ok=True, parents=True)
with open(path_to_repo_data / "well_map.json", "w") as f:
    json.dump(well_map, f)
# map the well to the well_map
df["Well"] = df["Well"].map(well_map)
df.head()


# In[7]:


print(f"There are {len(df['Well'].unique())} wells.")
print(f"There are {len(df['FOV'].unique())} fields of view.")
print(f"There are {len(df['Plate'].unique())} plates.")
print(f"There are {len(df['Date_Time'].unique())} unique time points.")
print("The times are:\n")
print(df["Date_Time"].unique())


# In[8]:


# check that there are
# 5 fovs * 5 channels * 96 wells = 2400 images per plate
fovs = 5
channels = 5
wells = 96
images_per_plate = fovs * channels * wells
# get the dirs in the data directory
dirs = glob.glob(str(pathlib.Path("../../../data/raw") / "*"))
dirs = [x for x in dirs if pathlib.Path(x).is_dir()]
plate_dict = {
    "plate_name": [],
    "num_files": [],
}
for dir in dirs:
    if pathlib.Path(dir).name != "platemaps":
        # get the files in the dir
        files = glob.glob(str(pathlib.Path(dir) / "*"))
        files = [x for x in files if pathlib.Path(x).is_file()]
        plate_dict["plate_name"].append(pathlib.Path(dir).name)
        plate_dict["num_files"].append(len(files))
plate_df = pd.DataFrame(plate_dict)
plate_df["correct_num_files"] = plate_df["num_files"] == images_per_plate
# sort by correct_num_files
plate_df.sort_values(by="correct_num_files", inplace=True)
plate_df.reset_index(drop=True, inplace=True)
plate_df


# ## Extract the metadata from one plate
# Each subsequent plate is a copy of the first at a differet time point and thus the metadata will remain the same.

# In[9]:


# get all files in the plate_id dir
files = glob.glob(str(pathlib.Path("../../../data/raw/20241026T164425_") / "*"))
files = [pathlib.Path(x).stem for x in files if pathlib.Path(x).is_file()]
df = pd.DataFrame(files, columns=["file_name"])
df["well"] = df["file_name"].str.split("F").str[0]
df["FOV"] = df["file_name"].str.split("F").str[1].str.split("T").str[0]
df["channel"] = df["file_name"].str.split("F").str[1].str.split("Z001").str[1]
# sort by well, FOV, channel
df.sort_values(by=["well", "FOV", "channel"], inplace=True)

# get the value counts for well, FOV
df[["well", "FOV"]].value_counts().sort_values()


# In[10]:


# get all files in the 20241025T045229_ dir
files = glob.glob(str(pathlib.Path("../../../data/raw/20241025T045229_") / "*"))
files = [pathlib.Path(x).stem for x in files if pathlib.Path(x).is_file()]
df = pd.DataFrame(files, columns=["file_name"])
df["well"] = df["file_name"].str.split("F").str[0]
df["FOV"] = df["file_name"].str.split("F").str[1].str.split("T").str[0]
df["channel"] = df["file_name"].str.split("F").str[1].str.split("Z001").str[1]
# sort by well, FOV, channel
df.sort_values(by=["well", "FOV", "channel"], inplace=True)

# get the value counts for well, FOV
df[["well", "FOV"]].value_counts().reset_index().sort_values(by=["count"])
