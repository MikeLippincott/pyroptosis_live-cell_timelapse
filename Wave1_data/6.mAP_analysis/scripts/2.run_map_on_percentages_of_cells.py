#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
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
import tqdm

# Suppress all RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

#


# In[2]:


if not in_notebook:
    # setup the argument parser
    parser = argparse.ArgumentParser(
        description="Generate a map for differing cell counts"
    )

    parser.add_argument(
        "--percentage", type=float, help="Percentage of wells to use for the map file"
    )
    parser.add_argument("--seed", type=int, help="Seed for the random number generator")
    parser.add_argument(
        "--shuffle", action="store_true", help="Shuffle the order of the wells"
    )
    # parse the arguments
    args = parser.parse_args()
    percentage = args.percentage
    set_seed = args.seed
    shuffle = args.shuffle
else:
    percentage = 0.4
    set_seed = 0
    shuffle = False

output_file = pathlib.Path(
    f"../results/mAP_cell_percentages/{percentage}_{set_seed}_{shuffle}.parquet"
)
output_file.parent.mkdir(exist_ok=True, parents=True)


# In[3]:


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


# In[4]:


sc_metadata_cols_to_drop = [
    "Metadata_ImageNumber",
    "Metadata_Cells_Number_Object_Number",
    "Metadata_Cytoplasm_Parent_Cells",
    "Metadata_Cytoplasm_Parent_Nuclei",
    "Metadata_ImageNumber_1",
    "Metadata_ImageNumber_2",
    "Metadata_ImageNumber_3",
    "Metadata_Nuclei_Number_Object_Number",
    "Metadata_Image_FileName_BF",
    "Metadata_Image_FileName_CL488",
    "Metadata_Image_FileName_CL561",
    "Metadata_Image_FileName_DNA",
    "Metadata_Image_FileName_GSDM",
    "Metadata_Image_PathName_BF",
    "Metadata_Image_PathName_CL488",
    "Metadata_Image_PathName_CL561",
    "Metadata_Image_PathName_DNA",
    "Metadata_Image_PathName_GSDM",
    "Metadata_Nuclei_Location_Center_X",
    "Metadata_Nuclei_Location_Center_Y",
    "Metadata_number_of_singlecells",
    "Metadata_FOV",
]


# In[5]:


data_file_path = pathlib.Path(
    "../../4.processing_profiled_features/data/preprocessed_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs_subset.parquet"
).resolve(strict=True)
df = pd.read_parquet(data_file_path)
df.reset_index(drop=True, inplace=True)
df = df[~df.Metadata_serum.str.contains("NuSerum")]

df.head()


# In[6]:


random.seed(set_seed)
subset_df = df.groupby(["Metadata_Time", "Metadata_treatment"]).apply(
    lambda x: x.sample(frac=percentage, random_state=set_seed),
    include_groups=False,
)
if shuffle:
    random.seed(0)
    # permutate the data
    for col in subset_df.columns:
        subset_df[col] = np.random.permutation(subset_df[col])
metadata_cols = [cols for cols in df.columns if "Metadata" in cols]
features_cols = [cols for cols in df.columns if "Metadata" not in cols]
features_cols = features_cols + ["Metadata_number_of_singlecells"]
aggregate_df = pycytominer.aggregate(
    population_df=df,
    strata=["Metadata_Well", "Metadata_Time"],
    features=features_cols,
    operation="median",
)
# Drop metadata columns
metadata_cols = [x for x in metadata_cols if x not in sc_metadata_cols_to_drop]

metadata_df = df[metadata_cols]
metadata_df = metadata_df.drop_duplicates()
aggregate_df = pd.merge(
    metadata_df, aggregate_df, on=["Metadata_Well", "Metadata_Time"]
)
dict_of_map_dfs = run_mAP_across_time(aggregate_df)
output_df = pd.concat(dict_of_map_dfs.values(), keys=dict_of_map_dfs.keys())
output_df.reset_index(inplace=True)
output_df.rename(columns={"level_0": "Metadata_Time"}, inplace=True)
# add the percentage of cells to the keys
output_df["percentage_of_cells"] = percentage
output_df["seed"] = set_seed
output_df["shuffle"] = shuffle
output_df.reset_index(drop=True, inplace=True)
output_df.to_parquet(output_file)
output_df.head()
