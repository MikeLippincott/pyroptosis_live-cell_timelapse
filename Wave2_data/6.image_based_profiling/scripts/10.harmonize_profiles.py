#!/usr/bin/env python
# coding: utf-8

# # Aggregate the single-cell profiles to the well level
# This notebook is not run as a large amount of RAM is needed to run it. It is provided for reference only.

# In[1]:


import os
import pathlib

import pandas as pd
from pycytominer import aggregate
from pycytominer.cyto_utils import output
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


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


# In[ ]:


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/platemap.csv"
).resolve()

image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
normalized_profiles_path = pathlib.Path(
    f"{image_base_dir}/10.normalized_profiles/{plate_name}/normalized_profiles.parquet"
).resolve(strict=True)
chammi_profiles_path = pathlib.Path(
    f"{image_base_dir}/9a.CHAMMI75_extracted_features/CHAMMI75_combined_sc_profiles.parquet"
).resolve(strict=True)

harmonized_profiles_path = pathlib.Path(
    f"{image_base_dir}/13.harmonized_profiles/harmonized_profiles.parquet"
).resolve()
harmonized_profiles_path.parent.mkdir(parents=True, exist_ok=True)


# In[3]:


norm_CP_df = pd.read_parquet(normalized_profiles_path)
chammi75_df = pd.read_parquet(chammi_profiles_path)
print("Shape of profiles:")
print(f"Normalized CP: {norm_CP_df.shape[0]}")
print(f"CHAMMI75: {chammi75_df.shape[0]}")


# In[ ]:


merged_df = pd.merge(
    norm_CP_df,
    chammi75_df,
    on=[
        "Metadata_Well_FOV",
        "Metadata_Time",
        "Metadata_Nuclei_Number_Object_Number",
        "Metadata_Cells_AreaShape_Center_X",
        "Metadata_Cells_AreaShape_Center_Y",
    ],
    how="left",
)

if norm_CP_df.shape[0] + chammi75_df.shape[0] != merged_df.shape[0]:
    print(
        "Warning: The number of rows in the merged dataframe does not equal the sum of the input dataframes. Please check for duplicates or missing values in the key columns."
    )
    print(f"Number of rows in normalized CP dataframe: {norm_CP_df.shape[0]}")
    print(f"Number of rows in CHAMMI75 dataframe: {chammi75_df.shape[0]}")
    print(f"Number of rows in merged dataframe: {merged_df.shape[0]}")

if merged_df.isnull().any().any():
    print(
        "Warning: There are missing values in the merged dataframe. Please check for mismatches in the key columns between the two dataframes."
    )

merged_df.to_parquet(harmonized_profiles_path, index=False)
merged_df.head()


# In[ ]:
