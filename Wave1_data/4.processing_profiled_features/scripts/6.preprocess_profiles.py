#!/usr/bin/env python
# coding: utf-8

# This notebook preprocesses the data to have correct time and treatment metadata.

# In[2]:


import argparse
import pathlib
from pprint import pprint

import pandas as pd

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


# In[8]:


normalized_dir = pathlib.Path("../data/normalized_data").resolve()
feature_selected_dir = pathlib.Path("../data/feature_selected_data").resolve()
aggregate_dir = pathlib.Path("../data/aggregated").resolve()
preprocessed_dir = pathlib.Path("../data/preprocessed_data").resolve()
preprocessed_dir.mkdir(exist_ok=True, parents=True)


# In[ ]:


input_data_dict = {
    "first_time": {
        "normalized": {
            "input_data": pathlib.Path(
                f"{normalized_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm.parquet"
            ).resolve(),
        },
        "selected": {
            "input_data": pathlib.Path(
                f"{feature_selected_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
            ).resolve(),
        },
        "aggregate_normalized": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_first_time_norm_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_first_time_norm_agg.parquet"
            ).resolve(),
        },
        "aggregate_selected": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"
            ).resolve(),
        },
    },
    "within_time": {
        "normalized": {
            "input_data": pathlib.Path(
                f"{normalized_dir}/live_cell_pyroptosis_wave1_sc_within_time_norm.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_within_time_norm.parquet"
            ).resolve(),
        },
        "selected": {
            "input_data": pathlib.Path(
                f"{feature_selected_dir}/live_cell_pyroptosis_wave1_sc_within_time_norm_fs.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_within_time_norm_fs.parquet"
            ).resolve(),
        },
        "aggregate_normalized": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_within_time_norm_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_within_time_norm_agg.parquet"
            ).resolve(),
        },
        "aggregate_selected": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_within_time_norm_fs_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_within_time_norm_fs_agg.parquet"
            ).resolve(),
        },
    },
    "pan_time": {
        "normalized": {
            "input_data": pathlib.Path(
                f"{normalized_dir}/live_cell_pyroptosis_wave1_sc_pan_time_norm.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_pan_time_norm.parquet"
            ).resolve(),
        },
        "selected": {
            "input_data": pathlib.Path(
                f"{feature_selected_dir}/live_cell_pyroptosis_wave1_sc_pan_time_norm_fs.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_sc_pan_time_norm_fs.parquet"
            ).resolve(),
        },
        "aggregate_normalized": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_pan_time_norm_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_pan_time_norm_agg.parquet"
            ).resolve(),
        },
        "aggregate_selected": {
            "input_data": pathlib.Path(
                f"{aggregate_dir}/live_cell_pyroptosis_wave1_pan_time_norm_fs_agg.parquet"
            ).resolve(),
            "output_data": pathlib.Path(
                f"{preprocessed_dir}/live_cell_pyroptosis_wave1_pan_time_norm_fs_agg.parquet"
            ).resolve(),
        },
    },
}

pprint(input_data_dict)


# In[ ]:


for dataset in input_data_dict:
    for data_type in input_data_dict[dataset]:
        data = pd.read_parquet(input_data_dict[dataset][data_type]["input_data"])

        # drop Wells N04, N06, N08, and N10 as they have no Hoechst stain
        data = data[~data["Metadata_Well"].str.contains("N04|N06|N08|N10")]
        # calculate the number of cells per well
        cells_per_well = data.groupby("Metadata_Well").size()
        data["Metadata_cells_per_well"] = data["Metadata_Well"].map(cells_per_well)

        if "aggregate" not in data_type:
            data = (
                data.groupby("Metadata_Well")
                .apply(lambda x: x.sample(samples_per_group))
                .reset_index(drop=True)
            )
            data.to_parquet(input_data_dict[dataset][data_type]["output_data"])
        elif data_subset:
            data = data.apply(lambda x: x.sample(samples_per_group)).reset_index(
                drop=True
            )
            subset_output = (
                input_data_dict[dataset][data_type]["output_data"].parent
                / f"{input_data_dict[dataset][data_type]['output_data'].stem}_subset.parquet"
            )
            data.to_parquet(subset_output)
        else:
            # over write the current parquet file
            data.to_parquet(input_data_dict[dataset][data_type]["output_data"])

        print(f"Preprocessed data for {dataset} has the shape: {data.shape}")


# In[ ]:


data.head()
