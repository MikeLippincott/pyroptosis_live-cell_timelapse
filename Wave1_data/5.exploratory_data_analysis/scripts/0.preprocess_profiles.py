#!/usr/bin/env python
# coding: utf-8

# This notebook preprocesses the data to have correct time and treatment metadata.

# In[1]:


import pathlib
from pprint import pprint

import pandas as pd
import pyarrow.parquet as pq


# In[ ]:


data_subset = False

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
    input_data_dict[dataset]["figure_dir"].mkdir(parents=True, exist_ok=True)
    if data_subset:
        subset_data_output_file_path = pathlib.Path(
            input_data_dict[dataset]["output_data_dir"]
            / f'{input_data_dict[dataset]["input_file_path"].stem}_subset_testing_data.parquet'
        ).resolve()
        data = pd.read_parquet(
            input_data_dict[dataset]["input_file_path"], columns=["Metadata_Well"]
        )
        data = data.groupby("Metadata_Well").head(50)
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

    if data_subset:
        data.to_parquet(subset_data_output_file_path)
    else:
        # over write the current parquet file
        data.to_parquet(input_data_dict[dataset]["input_file_path"])

    print(f"Preprocessed data for {dataset} has the shape: {data.shape}")

