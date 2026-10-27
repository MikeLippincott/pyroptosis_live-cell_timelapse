#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import os
import pathlib

import natsort
import pandas as pd
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


# In[2]:


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


# In[3]:


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data")

norm_agg_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/aggregate_profiles_from_normalized.parquet"
).resolve(strict=True)
norm_consensus_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/consensus_profiles_from_normalized.parquet"
).resolve(strict=True)
fs_agg_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/aggregate_profiles_from_feature_selected.parquet"
).resolve()
fs_consensus_profiles_path = pathlib.Path(
    f"{image_base_dir}/12.aggregate_profiles/{plate_name}/consensus_profiles_from_feature_selected.parquet"
).resolve()
norm_agg_profiles_path.parent.mkdir(exist_ok=True, parents=True)


# In[4]:


norm_agg_df = pd.read_parquet(norm_agg_profiles_path)


# In[7]:


norm_agg_df


# In[9]:


norm_agg_df["Metadata_Well"].unique()


# In[8]:


norm_agg_df["Metadata_Inducer"].unique()


# In[5]:


# plot the intensity profiles over time for nuclei, faceted by treatment
import re

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns


def dose_sort_key(treatment: str) -> tuple:
    """Pull the leading numeric dose values out of a treatment combo string for sorting."""
    matches = re.findall(r"([\d.]+)", treatment)
    return tuple(float(m) for m in matches) if matches else (0.0,)


compartment = "Nuclei"
channels = ["NucleoLive", "SYTOXGreen"]

norm_agg_df["Metadata_Treatment_combo"] = (
    norm_agg_df["Metadata_Inducer"].astype(str)
    + " "
    + norm_agg_df["Metadata_Inducer_dose"].astype(str)
    + " + "
    + norm_agg_df["Metadata_Inhibitor"].astype(str)
    + " "
    + norm_agg_df["Metadata_Inhibitor_dose"].astype(str)
)

treatment_order = sorted(
    norm_agg_df["Metadata_Treatment_combo"].unique(), key=dose_sort_key
)
palette = sns.color_palette("colorblind", n_colors=len(channels))

fig, axes = plt.subplots(
    len(treatment_order),
    len(channels),
    figsize=(5 * len(channels), 3 * len(treatment_order)),
    sharex=True,
)
for row_idx, treatment in enumerate(treatment_order):
    treatment_df = norm_agg_df[norm_agg_df["Metadata_Treatment_combo"] == treatment]
    for col_idx, channel in enumerate(channels):
        feature = f"{compartment}_Intensity_MeanIntensity_{channel}"
        ax = axes[row_idx, col_idx]
        if feature not in norm_agg_df.columns:
            ax.set_visible(False)
            continue
        sns.lineplot(
            data=treatment_df,
            x="Metadata_Time",
            y=feature,
            color=palette[col_idx],
            estimator="mean",
            errorbar="se",
            ax=ax,
        )
        ax.set_title(f"{treatment} / {channel}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Mean intensity (normalized)")
        ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
        ax.tick_params(axis="x", rotation=90)

fig.suptitle("Nuclei mean intensity profiles over time, faceted by treatment")
fig.tight_layout()
plt.show()


# In[6]:


# plot the max intensity profiles over time for nuclei, faceted by treatment
fig, axes = plt.subplots(
    len(treatment_order),
    len(channels),
    figsize=(5 * len(channels), 3 * len(treatment_order)),
    sharex=True,
)
for row_idx, treatment in enumerate(treatment_order):
    treatment_df = norm_agg_df[norm_agg_df["Metadata_Treatment_combo"] == treatment]
    for col_idx, channel in enumerate(channels):
        feature = f"{compartment}_Intensity_MaxIntensity_{channel}"
        ax = axes[row_idx, col_idx]
        if feature not in norm_agg_df.columns:
            ax.set_visible(False)
            continue
        sns.lineplot(
            data=treatment_df,
            x="Metadata_Time",
            y=feature,
            color=palette[col_idx],
            estimator="mean",
            errorbar="se",
            ax=ax,
        )
        ax.set_title(f"{treatment} / {channel}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Max intensity (normalized)")
        ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
        ax.tick_params(axis="x", rotation=90)

fig.suptitle("Nuclei max intensity profiles over time, faceted by treatment")
fig.tight_layout()
plt.show()
