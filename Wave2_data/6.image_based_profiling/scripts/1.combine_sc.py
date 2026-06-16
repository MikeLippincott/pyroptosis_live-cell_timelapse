#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[ ]:


import os
import pathlib

import natsort
import numpy as np
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

# In[ ]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{root_dir}/data").resolve(strict=True)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
converted_profiles_dir = pathlib.Path(
    f"{image_base_dir}/4.converted_profiles/"
).resolve(strict=True)

combined_profiles_path = pathlib.Path(
    f"{image_base_dir}/5.combined_profiles/"
).resolve()
combined_profiles_path.mkdir(exist_ok=True)


# In[ ]:


# well_fov_timepoints - get all the well_fov_timepoints that we have extracted features for
converted_profiles = [
    x for x in tqdm.tqdm(converted_profiles_dir.glob("*")) if x.is_dir()
]
# sort the converted profiles in natural order
converted_profiles = natsort.natsorted(converted_profiles)
# get all the converted profile parquet files as a list of paths to use downstream
converted_profiles = [
    list(x.glob("**/*.parquet"))[0]
    for x in tqdm.tqdm(
        converted_profiles,
        desc="Getting converted profiles",
        total=len(converted_profiles),
    )
    if len(list(x.glob("**/*.parquet"))) > 0
]
converted_profiles = natsort.natsorted(converted_profiles)
print(f"Number of converted profiles: {len(converted_profiles)}")


# In[ ]:


# check if any of the parquet files have buffer 0
# ArrowInvalid: Could not open Parquet input source '<Buffer>': Parquet file size is 0 bytes
# find the files and print them
total = len(converted_profiles)
zero_size_files = 0
for parquet_file in tqdm.tqdm(converted_profiles):
    if parquet_file.stat().st_size == 0:
        zero_size_files += 1
        # # unlink the file
        # if parquet_file.is_file():
        #     parquet_file.unlink()
        # elif parquet_file.is_dir():
        #     shutil.rmtree(parquet_file)

print(f"Total files: {total}, Empty files: {zero_size_files}")


# In[ ]:


converted_profiles_df = pd.DataFrame({"converted_profile_path": converted_profiles})
converted_profiles_df["well_fov_time"] = converted_profiles_df[
    "converted_profile_path"
].apply(lambda x: x.parent.name)
converted_profiles_df["well_fov"] = converted_profiles_df[
    "converted_profile_path"
].apply(lambda x: ("_").join(x.parent.name.split("_")[:2]))
converted_profiles_df


# In[ ]:


# loop through unique well fovs then combine all timepoints for each well fov and save as a single parquet file
for well_fov, group in tqdm.tqdm(
    converted_profiles_df.groupby("well_fov"),
    desc="Combining profiles",
    total=converted_profiles_df["well_fov"].nunique(),
):
    well_fov_path = pathlib.Path(
        f"{combined_profiles_path}/well_fovs_combined/{well_fov}.parquet"
    )
    well_fov_path.parent.mkdir(parents=True, exist_ok=True)
    if not well_fov_path.exists():
        # get the converted profile paths for the current well fov time
        tmp_df = converted_profiles_df[converted_profiles_df["well_fov"] == well_fov]
        # read each parquet file and concatenate them into a single dataframe
        combined_df = pd.concat(
            [pd.read_parquet(x) for x in tmp_df["converted_profile_path"]],
            ignore_index=True,
        )
        # fix mixed types in object columns before saving to parquet
        for col in combined_df.select_dtypes(include="object").columns:
            combined_df[col] = combined_df[col].astype(str)
        # save the combined dataframe as a parquet file
        combined_df.to_parquet(well_fov_path)


# # not enough RAM on machine to perform this - must use HPC

# In[ ]:


# concat all the combined well fov parquet files into a single dataframe and save as a parquet file
combined_well_fov_paths = list(
    (combined_profiles_path / "well_fovs_combined").glob("*.parquet")
)
combined_well_fov_paths = natsort.natsorted(combined_well_fov_paths)
combined_df = pd.concat(
    [pd.read_parquet(x) for x in combined_well_fov_paths], ignore_index=True
)
