#!/usr/bin/env python
# coding: utf-8

# # Aggregate the single-cell profiles to the well level
# This notebook is not run as a large amount of RAM is needed to run it. It is provided for reference only.

# In[1]:


import argparse
import os
import pathlib

import natsort
import pandas as pd
from pyarrow import parquet as pq
from pycytominer import aggregate
from pycytominer.cyto_utils import infer_cp_features, output
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


# In[2]:


def agg_calls(
    profile_path: pathlib.Path, strata: list, metadata_cols_to_keep: list = None
) -> pd.DataFrame:
    """
    Perform aggregation of profile data based on specified strata
    using pycytominer's aggregate function

    Parameters
    ----------
    profile_path : pathlib.Path
        Path to the profile data file (parquet format)
    strata : list
        List of columns to use for aggregation
    metadata_cols_to_keep : list, optional
        List of metadata columns to keep in the final DataFrame

    Returns
    -------
    pd.DataFrame
        Aggregated profile data with metadata columns preserved
    """
    ###########################################################################################
    # Normalized aggregate data
    ###########################################################################################
    # Load the normalized data
    df = pd.read_parquet(profile_path)
    features_cols = infer_cp_features(df)
    metadata_cols = [cols for cols in df.columns if cols not in features_cols]

    aggregate_df = aggregate(
        profiles=df,
        strata=strata,
        features=features_cols,
        operation="median",
    )
    # Drop metadata columns
    if metadata_cols_to_keep is not None:
        metadata_cols = metadata_cols_to_keep + strata
    metadata_df = df[metadata_cols]
    metadata_df = metadata_df.drop_duplicates(subset=strata).reset_index(drop=True)

    norm_aggregate_df = pd.merge(metadata_df, aggregate_df, on=strata)
    return norm_aggregate_df


# In[3]:


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


# In[4]:


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
    f"{image_base_dir}/10.normalized_profiles/{plate_name}"
).resolve(strict=True)
feature_selected_profiles_path = pathlib.Path(
    f"{image_base_dir}/11.feature_selected_profiles/{plate_name}/"
).resolve(strict=True)

norm_agg_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/aggregate_profiles_from_normalized.parquet"
).resolve()
norm_consensus_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/consensus_profiles_from_normalized.parquet"
).resolve()
fs_agg_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/aggregate_profiles_from_feature_selected.parquet"
).resolve()
fs_consensus_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/consensus_profiles_from_feature_selected.parquet"
).resolve()
norm_agg_profiles_path.parent.mkdir(exist_ok=True, parents=True)


# In[5]:


norm_profiles_path_list = natsort.natsorted(
    list(normalized_profiles_path.glob("*.parquet")), key=lambda x: x.stem
)
fs_profiles_path_list = natsort.natsorted(
    list(feature_selected_profiles_path.glob("*.parquet")), key=lambda x: x.stem
)


# ## Set the columns to keep, drop, and the strata to aggregate by

# In[6]:


columns = pq.ParquetFile(norm_profiles_path_list[0]).schema.names
metadata_cols_to_keep = [
    "Metadata_Inducer1",
    "Metadata_Inducer1_dose",
    "Metadata_Inducer1_unit",
    "Metadata_Inducer2",
    "Metadata_Inducer2_dose",
    "Metadata_Inducer2_unit",
    "Metadata_Inhibitor",
    "Metadata_Inhibitor_dose",
    "Metadata_Inhibitor_unit",
    "Metadata_Well_FOV",
    "Metadata_FOV",
    "Metadata_Well_FOV_Time",
    "Metadata_ImageNumber",
    "Metadata_Image_URL_CL488",
    "Metadata_Image_URL_CL640",
    "Metadata_Image_URL_NucleoLive",
    "Metadata_Image_URL_SYTOXGreen",
    "Metadata_single_cell_count",
]
compartment_list = ["Cytoplasm", "Nuclei", "Cells"]
center_xy_cols = [
    x
    for x in columns
    if x.startswith("Metadata_")
    if any(c in x for c in compartment_list)
    and "cqc" not in x
    and "_center_" in x.lower()
]
cqc_cols = [x for x in columns if x.startswith("Metadata_") and "cqc" in x]
metadata_cols_to_keep = metadata_cols_to_keep + cqc_cols + center_xy_cols
agg_strata = ["Metadata_Well", "Metadata_Time"]
consensus_strata = [
    "Metadata_Inducer1",
    "Metadata_Inducer1_dose",
    "Metadata_Inducer2",
    "Metadata_Inducer2_dose",
    "Metadata_Inhibitor",
    "Metadata_Inhibitor_dose",
    "Metadata_Time",
]


# These cells take incredibly long to run and thus are not run in the notebook.
# They are provided for to be run in the nbconverted script.

# ## Normalized profile agg and consensus profile generation

# In[ ]:


agg_output_dict = {
    "well_fov": [],
    "agg": [],
    "consensus": [],
}
for norm_profile_path in tqdm.tqdm(
    norm_profiles_path_list, leave=False, total=len(norm_profiles_path_list)
):
    well_fov = norm_profile_path.stem.replace("_normalized", "")
    agg_output_dict["well_fov"].append(well_fov)
    agg_df = agg_calls(profile_path=norm_profile_path, strata=agg_strata)
    consensus_df = agg_calls(profile_path=norm_profile_path, strata=consensus_strata)
    print(
        f"Shape of agg_df: {agg_df.shape}, Shape of consensus_df: {consensus_df.shape}"
    )
    agg_output_dict["agg"].append(agg_df)
    agg_output_dict["consensus"].append(consensus_df)
agg_norm_all_df = pd.concat(agg_output_dict["agg"], ignore_index=True)
consensus_norm_all_df = pd.concat(agg_output_dict["consensus"], ignore_index=True)
print(agg_norm_all_df.shape)
print(consensus_norm_all_df.shape)
for df in (agg_norm_all_df, consensus_norm_all_df):
    df["Metadata_Time"] = pd.to_numeric(df["Metadata_Time"], errors="coerce")
    df["Metadata_Time"] = df["Metadata_Time"].astype("float64").astype("int16")

agg_norm_all_df.to_parquet(norm_agg_profiles_path, index=False)
consensus_norm_all_df.to_parquet(norm_consensus_profiles_path, index=False)

# clean up a bit
# not that it matters because del and gc in python
# is essentially fake
# but this makes me feel better
# kind of like recycling plastics...
del agg_output_dict, agg_norm_all_df, consensus_norm_all_df


# ## Feature selection profile agg and consensus profile generation

# In[ ]:


agg_output_dict = {
    "well_fov": [],
    "agg": [],
    "consensus": [],
}
for fs_profile_path in tqdm.tqdm(
    fs_profiles_path_list, leave=False, total=len(fs_profiles_path_list)
):
    well_fov = fs_profile_path.stem.replace("_normalized", "")
    agg_output_dict["well_fov"].append(well_fov)
    agg_df = agg_calls(profile_path=fs_profile_path, strata=agg_strata)
    consensus_df = agg_calls(profile_path=fs_profile_path, strata=consensus_strata)
    agg_output_dict["agg"].append(agg_df)
    agg_output_dict["consensus"].append(consensus_df)
agg_fs_all_df = pd.concat(agg_output_dict["agg"], ignore_index=True)
consensus_all_df = pd.concat(agg_output_dict["consensus"], ignore_index=True)
print(agg_fs_all_df.shape)
print(consensus_all_df.shape)
for df in (agg_norm_all_df, consensus_norm_all_df):
    df["Metadata_Time"] = pd.to_numeric(df["Metadata_Time"], errors="coerce")
    df["Metadata_Time"] = df["Metadata_Time"].astype("float64").astype("int16")
agg_fs_all_df.to_parquet(fs_agg_profiles_path, index=False)
consensus_all_df.to_parquet(fs_consensus_profiles_path, index=False)
