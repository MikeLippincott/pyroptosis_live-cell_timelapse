#!/usr/bin/env python
# coding: utf-8

# This notebook preprocesses the data to have correct time and treatment metadata.

# In[5]:


import argparse
import pathlib
from pprint import pprint

import pandas as pd
import pyarrow.parquet as pq


# In[ ]:


# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False

if not in_notebook:
    print("Running as script")
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--samples_per_group",
        type=int,
        default=25,
        help="Number of samples per group",
    )
    parser.add_argument(
        "--data_subset",
        action="store_true",
        help="Use a subset of the data",
    )

    args = parser.parse_args()
    samples_per_group = args.samples_per_group
    data_subset = args.data_subset
else:
    print("Running in a notebook")
    data_subset = True
    samples_per_group = 25


# In[ ]:


# path to the data
feature_selected_profiles_data_dir = pathlib.Path(
    "../../4.processing_profiled_features/data/feature_selected_data"
).resolve(strict=True)
list_of_files = list(feature_selected_profiles_data_dir.glob("*.parquet"))

input_data_dict = {
    "first_time": {
        "input_file_path": list_of_files[0],
        "output_data_dir": pathlib.Path("../data/first_time").resolve(),
        "figure_dir": pathlib.Path("../figures/first_time").resolve(),
    },
    "within_time": {
        "input_file_path": list_of_files[1],
        "output_data_dir": pathlib.Path("../data/within_time").resolve(),
        "figure_dir": pathlib.Path("../figures/within_time").resolve(),
    },
    "pan_time": {
        "input_file_path": list_of_files[2],
        "output_data_dir": pathlib.Path("../data/pan_time").resolve(),
        "figure_dir": pathlib.Path("../figures/pan_time").resolve(),
    },
}
pprint(input_data_dict)


# In[ ]:


for dataset in input_data_dict:
    input_data_dict[dataset]["output_data_dir"].mkdir(parents=True, exist_ok=True)
    if data_subset and "aggregate" not in dataset:
        subset_data_output_file_path = pathlib.Path(
            input_data_dict[dataset]["output_data_dir"]
            / f'{input_data_dict[dataset]["input_file_path"].stem}_subset_testing_data.parquet'
        ).resolve()
        data = pd.read_parquet(
            input_data_dict[dataset]["input_file_path"], columns=["Metadata_Well"]
        )
        data_df = data.groupby("Metadata_Well").apply(
            lambda x: x.sample(min(len(x), samples_per_group), random_state=0)
        )

        # get the indexes of the data
        data_idx = data.index
        data = pd.concat(
            [
                pd.read_parquet(
                    input_data_dict[dataset]["input_file_path"], columns=[col]
                ).iloc[data_idx]
                for col in pq.read_schema(
                    input_data_dict[dataset]["input_file_path"]
                ).names
            ],
            axis=1,
        )
        # save the subset data
        data.to_parquet(subset_data_output_file_path)
        data.head()
    else:
        data = pd.read_parquet(input_data_dict[dataset]["input_file_path"])
        data.head()

    # perform preprocessing on each data
    # sort the time and replace with 1, 2, 3, 4
    time_mapping = {
        time: i for i, time in enumerate(data["Metadata_Plate"].sort_values().unique())
    }
    # check if the new columns exist, if so drop them
    if "Metadata_treatment_serum" in data.columns:
        data.drop(columns=["Metadata_treatment_serum"], inplace=True)
    if "Metadata_Time" in data.columns:
        data.drop(columns=["Metadata_Time"], inplace=True)
    # Combine all new columns at once to avoid fragmentation
    new_columns = pd.DataFrame(
        {
            "Metadata_treatment_serum": data["Metadata_treatment"]
            + " "
            + data["Metadata_serum"],
            "Metadata_Time": data["Metadata_Plate"].map(time_mapping),
        }
    )
    data = pd.concat([data, new_columns], axis=1)

    # drop Wells N04, N06, N08, and N10 as they have no Hoechst stain

    data = data[~data["Metadata_Well"].str.contains("N04|N06|N08|N10")]

    if data_subset:
        data.to_parquet(subset_data_output_file_path)
    else:
        # over write the current parquet file
        data.to_parquet(input_data_dict[dataset]["input_file_path"])

    print(f"Preprocessed data for {dataset} has the shape: {data.shape}")


# In[ ]:


data.head()

