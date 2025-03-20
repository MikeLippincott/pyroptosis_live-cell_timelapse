#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib
import random

import numpy as np
import pandas as pd
from copairs import map
from copairs.matching import assign_reference_index

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False
import warnings

import pycytominer.aggregate

# Suppress all RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
import itertools

#


# In[2]:


def run_mAP_across_time(
    df: pd.DataFrame,
):
    """
    Run mAP across timepoints specifies and hardcoded columns for this data

    Parameters
    ----------
    df : pd.DataFrame
        An aggregated dataframe with metadata and features and temporal information

    Returns
    -------
    dict
        A dictionary of dataframes with the mAP results for each
        timepoint.
    """
    unique_timepoints = df.Metadata_Time.unique()
    dict_of_map_dfs = {}
    for timepoint in unique_timepoints:
        single_time_df = df.loc[df.Metadata_Time == timepoint]
        reference_col = "Metadata_reference_index"
        df_activity = assign_reference_index(
            single_time_df,
            "Metadata_treatment == 'DMSO CTL'",
            reference_col=reference_col,
            default_value=-1,
        )
        pos_sameby = ["Metadata_treatment", reference_col]
        pos_diffby = []
        neg_sameby = []
        neg_diffby = ["Metadata_treatment", reference_col]
        metadata = df_activity.filter(regex="Metadata")
        profiles = df_activity.filter(regex="^(?!Metadata)").values

        activity_ap = map.average_precision(
            metadata, profiles, pos_sameby, pos_diffby, neg_sameby, neg_diffby
        )

        activity_ap = activity_ap.query("Metadata_treatment != 'DMSO CTL'")
        activity_map = map.mean_average_precision(
            activity_ap, pos_sameby, null_size=1000000, threshold=0.05, seed=0
        )
        activity_map["-log10(p-value)"] = -activity_map["corrected_p_value"].apply(
            np.log10
        )
        # flatten the multi-index columns to make it easier to work with
        dict_of_map_dfs[timepoint] = activity_map
    return dict_of_map_dfs


# In[3]:


data_file_path = pathlib.Path(
    "../../4.processing_profiled_features/data/preprocessed_data/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"
).resolve(strict=True)
pathlib.Path("../results").mkdir(exist_ok=True)
aggregate_df = pd.read_parquet(data_file_path)
aggregate_df.reset_index(drop=True, inplace=True)
aggregate_df = aggregate_df[~aggregate_df.Metadata_serum.str.contains("NuSerum")]
aggregate_df.reset_index(drop=True, inplace=True)
print(aggregate_df.shape)
# drop rows with nan in features (non Metadata)
aggregate_df = aggregate_df.dropna(
    subset=aggregate_df.filter(regex="^(?!Metadata)").columns
)
print(aggregate_df.shape)
aggregate_df.head()


# In[4]:


# get the non metadata columns
metadata_cols = [cols for cols in aggregate_df.columns if "Metadata" in cols]
features_cols = [cols for cols in aggregate_df.columns if "Metadata" not in cols]
# drop features that contain AreaShape in the feature name
non_feature_cols = [cols for cols in features_cols if "AreaShape" in cols]
non_feature_cols = (
    non_feature_cols
    + [col for col in features_cols if "Location" in col]
    + [col for col in features_cols if "Neighbors" in col]
)
correlation_cols = [col for col in features_cols if "Correlation" in col]
features_cols = [cols for cols in features_cols if cols not in non_feature_cols]
features_cols = [cols for cols in features_cols if cols not in correlation_cols]
df = pd.DataFrame(features_cols, columns=["features"])

df[
    [
        "Compartment",
        "Feature_type",
        "Measurement",
        "Channel",
        "Feature_info1",
        "Feature_info2",
        "Feature_info3",
    ]
] = df["features"].str.split("_", expand=True)
df.head()


# In[5]:


# create a dictionary of loadable features for each channel
loadable_features = {}
for channel in df.Channel.unique():
    channel_df = df.query("Channel == @channel")
    loadable_features[channel] = channel_df.features.tolist()
loadable_features["None"] = non_feature_cols
loadable_features["All"] = [
    cols for cols in aggregate_df.columns if "Metadata" not in cols
]


# In[6]:


unique_channels = df["Channel"].unique().tolist()
# unique_channels = unique_channels + ['None']
# channel combinations
channel_combinations = []
for i in range(1, len(unique_channels) + 1):
    channel_combinations.extend(list(itertools.combinations(unique_channels, i)))
channel_combinations = [list(comb) for comb in channel_combinations]
channel_combinations = channel_combinations + [["None"]]


# In[7]:


channel_combo_output_dict = {}
for shuffle in [True, False]:
    for channel_combination in channel_combinations:
        features_to_load = []
        features_to_load.append(metadata_cols)
        if len(channel_combination) == 5:
            channel_combination = ["All"]
        elif channel_combination == ["None"]:
            features_to_load.append(loadable_features["None"])
        else:
            for channel in channel_combination:
                features_to_load.append(loadable_features[channel])
            features_to_load.append(loadable_features["None"])

        features_to_load = list(itertools.chain(*features_to_load))
        temporary_df = aggregate_df[features_to_load]
        if shuffle:
            shuffle = "shuffled"
            random.seed(0)
            # permutate the data
            for col in temporary_df.columns:
                if "Metadata_Time" in col or "Metadata_treatment" in col:
                    pass
                else:
                    temporary_df[col] = np.random.permutation(temporary_df[col])
        else:
            shuffle = "non_shuffled"
        dict_of_map_dfs = run_mAP_across_time(temporary_df)
        df = pd.concat(dict_of_map_dfs.values(), keys=dict_of_map_dfs.keys())
        df.reset_index(inplace=True)
        df["Channel"] = "_".join(channel_combination)
        df["shuffle"] = shuffle
        channel_combo_output_dict["_".join(channel_combination)] = df


# In[8]:


final_df = pd.concat(
    channel_combo_output_dict.values(), keys=channel_combo_output_dict.keys()
)
final_df.reset_index(inplace=True, drop=True)
# save the output to a file
final_df.to_parquet("../results/mAP_across_channels.parquet")
final_df.head()
