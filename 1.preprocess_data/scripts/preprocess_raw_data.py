#!/usr/bin/env python
# coding: utf-8

# In[1]:


import glob
import pathlib
import shutil

import pandas as pd
import tqdm

# In[2]:


# absolute path to the raw data directory only works on this machine
path_to_raw_data = pathlib.Path(
    "/home/lippincm/Desktop/18TB/Saguaro_pyroptosis_wave1/"
).resolve(strict=True)

# repository data directory to access the data faster
path_to_repo_data = pathlib.Path("../../data/raw/").resolve()
path_to_repo_data.mkdir(exist_ok=True, parents=True)

# recurse through the directory and find all the .tif or .tiff files
list_of_files = glob.glob(str(path_to_raw_data / "**/Image/*.tif*"), recursive=True)
print(f"Found {len(list_of_files)} files")


# In[3]:


# copy the files to the repository data directory
for file in tqdm.tqdm(list_of_files):
    file_path = pathlib.Path(file)
    file_parent = file_path.parent
    file_parent_path = path_to_repo_data / pathlib.Path(str(file_parent).split("/")[-2])
    file_parent_path.mkdir(exist_ok=True, parents=True)
    new_file_path = file_parent_path / file_path.name
    # copy the file to the repository data directory
    shutil.copy(file_path, new_file_path)


# In[4]:


# verify that the number of images in are the same as the number of files copied
list_of_new_files = glob.glob(str(path_to_repo_data / "**/*.tif*"), recursive=True)
print(f"There were {len(list_of_files)} original files")
print(f"We copied {len(list_of_new_files)} files")
assert len(list_of_files) == len(list_of_new_files)


# In[5]:


# make a df out of the file names
df = pd.DataFrame(list_of_new_files, columns=["file_path"])
df.insert(0, "file_name", df["file_path"].apply(lambda x: pathlib.Path(x).name))
df.insert(0, "Plate", df["file_path"].apply(lambda x: x.split("/")[7]))
df.insert(0, "Well", df["file_name"].apply(lambda x: x.split("F")[0].split("W")[-1]))
df.insert(0, "FOV", df["file_name"].apply(lambda x: x.split("T")[0].split("F")[-1]))
df.drop("file_path", axis=1, inplace=True)
df.drop("file_name", axis=1, inplace=True)
# sort by plate, well, and FOV
df.sort_values(by=["Plate", "Well", "FOV"], inplace=True)
df.head()


# In[6]:


print(f"There are {len(df['Well'].unique())} wells.")
print(f"There are {len(df['FOV'].unique())} fields of view.")
print(f"There are {len(df['Plate'].unique())} plates.")
