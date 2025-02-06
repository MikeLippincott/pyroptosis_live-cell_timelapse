#!/usr/bin/env python
# coding: utf-8

# This notebook preprocesses the data to have correct time and treatment metadata.

# In[1]:


import pathlib
from pprint import pprint

import pandas as pd
import pyarrow.parquet as pq


# In[2]:


data_subset = True
samples_per_group = 25

# path to the data
feature_selected_profiles_data_dir = pathlib.Path(
    "../../4.processing_profiled_features/data/feature_selected_data"
).resolve(strict=True)
list_of_files = list(feature_selected_profiles_data_dir.glob("*.parquet"))

input_data_dict = {
    # "first_time": {
    #     "input_file_path": list_of_files[0],
    #     "output_data_dir": pathlib.Path("../data/first_time").resolve(),
    #     "figure_dir": pathlib.Path("../figures/first_time").resolve(),
    # },
    # "within_time": {
    #     "input_file_path": list_of_files[1],
    #     "output_data_dir": pathlib.Path("../data/within_time").resolve(),
    #     "figure_dir": pathlib.Path("../figures/within_time").resolve(),
    # },
    # "pan_time": {
    #     "input_file_path": list_of_files[2],
    #     "output_data_dir": pathlib.Path("../data/pan_time").resolve(),
    #     "figure_dir": pathlib.Path("../figures/pan_time").resolve(),
    # },
    "aggregated_norm": {
        "input_file_path": pathlib.Path(
            "../data/aggregated/live_cell_pyroptosis_wave1_first_time_norm_agg.parquet"
        ).resolve(),
        "output_data_dir": pathlib.Path("../data/preprocessed").resolve(),
    },
}
pprint(input_data_dict)


# In[6]:


# show all the columns
pd.set_option("display.max_columns", None)


# In[7]:


df = pd.read_parquet(input_data_dict["aggregated_norm"]["input_file_path"])
print(df.shape)
df.head()


# In[5]:


for dataset in input_data_dict:
    input_data_dict[dataset]["output_data_dir"].mkdir(parents=True, exist_ok=True)
    if data_subset:
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

