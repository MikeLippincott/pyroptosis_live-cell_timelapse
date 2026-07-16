#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import os
import pathlib
from collections import defaultdict

import duckdb
import natsort
import numpy as np
import pandas as pd
import polars as pl
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm


# In[ ]:


if in_notebook:
    import tqdm.notebook as tqdm

    plate_name = "plate_2"
else:
    import tqdm

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    plate_name = args.plate_name


# In[2]:


def read_and_cast(path: pathlib.Path, conflicts: list[str]) -> pl.DataFrame:
    """
    Cast types for the dfs such that they are all similar

    Parameters
    ----------
    path : pathlib.Path
        path of the parquet file to read
    conflicts : list[str]
        Expected conflicting columns that should be cast to Float64. Only casts if the column is present in the df.

    Returns
    -------
    pl.DataFrame
        the read and casted dataframe
    """
    df = pl.read_parquet(path)
    cast_exprs = [
        pl.col(col).cast(pl.Float64) for col in conflicts if col in df.columns
    ]
    if cast_exprs:
        df = df.with_columns(cast_exprs)
    return df


# ## Set paths and variables

# In[ ]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{root_dir}/data").resolve(strict=True)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
converted_profiles_dir = pathlib.Path(
    f"{image_base_dir}/5.converted_profiles/{plate_name}"
).resolve(strict=True)

combined_profiles_path = pathlib.Path(
    f"{image_base_dir}/6.combined_profiles/{plate_name}"
).resolve()
combined_profiles_path.mkdir(exist_ok=True)


# In[4]:


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


# In[5]:


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


# In[6]:


converted_profiles_df = pd.DataFrame({"converted_profile_path": converted_profiles})
converted_profiles_df["well_fov_time"] = converted_profiles_df[
    "converted_profile_path"
].apply(lambda x: x.parent.name)
converted_profiles_df["well_fov"] = converted_profiles_df[
    "converted_profile_path"
].apply(lambda x: ("_").join(x.parent.name.split("_")[:2]))
converted_profiles_df


# In[7]:


converted_profiles_df = converted_profiles_df.loc[
    converted_profiles_df["well_fov"] == "C2_3"
]
converted_profiles_df


# In[11]:


converted_profiles_df.loc[converted_profiles_df["well_fov_time"] == "C2_3_T0001"]


# In[8]:


# loop through unique well fovs then combine all timepoints for each well fov and save as a single parquet file
for well_fov, group in tqdm.tqdm(
    converted_profiles_df.groupby("well_fov"),
    desc="Combining profiles",
    total=converted_profiles_df["well_fov"].nunique(),
):
    well_fov_path = pathlib.Path(f"{combined_profiles_path}/{well_fov}.parquet")
    well_fov_path.parent.mkdir(parents=True, exist_ok=True)
    if well_fov_path.exists():
        continue
    # if not well_fov_path.exists():
    # get the converted profile paths for the current well fov time
    tmp_df = converted_profiles_df[converted_profiles_df["well_fov"] == well_fov]

    # read each parquet file and concatenate them into a single dataframe
    combined_well_fov_paths = tmp_df["converted_profile_path"].tolist()
    combined_well_fov_paths = [str(x) for x in combined_well_fov_paths]

    # Step 1: find all conflicting columns
    schemas = [pl.read_parquet_schema(p) for p in combined_well_fov_paths]

    col_types = defaultdict(set)
    for schema in schemas:
        for col, dtype in schema.items():
            col_types[col].add(dtype)

    conflicts = {col: types for col, types in col_types.items() if len(types) > 1}
    if conflicts:
        print(f"Conflicting columns found in {well_fov}:")
        for col, types in conflicts.items():
            print(f"  Column: {col}, Types: {types}")

    # Step 2: read each file, casting conflicts to Float64 before concat

    frames = [
        read_and_cast(p, conflicts)
        for p in tqdm.tqdm(
            combined_well_fov_paths, leave=False, desc="Reading and casting files"
        )
    ]
    combined_df = pl.concat(
        frames, how="diagonal"
    )  # diagonal handles missing columns too
    # fix mixed types in object columns before saving to parquet
    # for col in combined_df.select_dtypes(include="object").columns:
    #     combined_df[col] = combined_df[col].astype(str)
    # for col in combined_df.columns:
    #     if col == "Metadata_Cells_Number_Object_Number":
    #         combined_df[col] = combined_df[col].astype(int)
    # save the combined dataframe as a parquet file
    combined_df.write_parquet(well_fov_path)


# In[9]:


combined_df = pd.read_parquet(well_fov_path)


# In[10]:


combined_df


# In[ ]:
