#!/usr/bin/env python
# coding: utf-8

# This notebook explores the data at hand to understand the distribution and shape, as well as perform some pca and UMAP analysis to understand the data better.

# In[1]:


import pathlib
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
import umap
from sklearn.decomposition import PCA


# In[ ]:


figure_dir = pathlib.Path("../figures").resolve()
output_data_dir = pathlib.Path("../data").resolve()
figure_dir.mkdir(parents=True, exist_ok=True)
output_data_dir.mkdir(parents=True, exist_ok=True)

data_subset = False


# In[ ]:


input_data_dict = {
    "first_time": {
        "input_file_path_subset": pathlib.Path(
            "../data/first_time/live_cell_pyroptosis_wave1_sc_first_time_norm_fs_subset_testing_data.parquet"
        ).resolve(),
        "input_file_path": pathlib.Path(
            "../../4.processing_profiled_features/data/feature_selected_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
        ).resolve(),
        "output_data_dir": pathlib.Path("../data/first_time").resolve(),
        "figure_dir": pathlib.Path("../figures/first_time").resolve(),
    },
    "pan_time": {
        "input_file_path_subset": pathlib.Path(
            "../data/pan_time/live_cell_pyroptosis_wave1_sc_pan_time_norm_fs_subset_testing_data.parquet"
        ).resolve(),
        "input_file_path": pathlib.Path(
            "../../4.processing_profiled_features/data/feature_selected_data/live_cell_pyroptosis_wave1_sc_pan_time_norm_fs.parquet"
        ).resolve(),
        "output_data_dir": pathlib.Path("../data/pan_time").resolve(),
        "figure_dir": pathlib.Path("../figures/pan_time").resolve(),
    },
    "within_time": {
        "input_file_path_subset": pathlib.Path(
            "../data/within_time/live_cell_pyroptosis_wave1_sc_within_time_norm_fs_subset_testing_data.parquet"
        ).resolve(),
        "input_file_path": pathlib.Path(
            "../../4.processing_profiled_features/data/feature_selected_data/live_cell_pyroptosis_wave1_sc_within_time_norm_fs.parquet"
        ).resolve(),
        "output_data_dir": pathlib.Path("../data/within_time").resolve(),
        "figure_dir": pathlib.Path("../figures/within_time").resolve(),
    },
}
pprint(input_data_dict)


# In[ ]:


random_state = 0
umap_reducer = umap.UMAP(
    n_neighbors=15, min_dist=0.1, n_components=2, random_state=random_state
)
max_pca_components = 100
scree_pca = PCA(n_components=max_pca_components)
pca_reducer = PCA(n_components=2, random_state=random_state)

for data_set_name in input_data_dict.keys():
    if data_subset:
        data_df = pd.read_parquet(
            input_data_dict[data_set_name]["input_file_path_subset"]
        )
    else:
        data_df = pd.read_parquet(input_data_dict[data_set_name]["input_file_path"])
    # set the UMAP parameters
    # separate the data into features and labels
    metadata_columns = data_df.columns[data_df.columns.str.contains("Metadata")]
    metadata_columns_df = data_df[metadata_columns]
    features_df = data_df.drop(metadata_columns, axis=1)
    features_df = features_df.fillna(0)
    print(
        f"Original data shape: {data_df.shape}, features shape: {features_df.shape}, and metadata shape: {metadata_columns_df.shape}"
    )

    # fit the UMAP model
    umap_embedding = umap_reducer.fit_transform(features_df)
    umap_embedding_df = pd.DataFrame(umap_embedding, columns=["UMAP0", "UMAP1"])
    umap_embedding_df = pd.concat(
        [metadata_columns_df.reset_index(drop=True), umap_embedding_df], axis=1
    )

    umap_embeddings_file_path = pathlib.Path(
        input_data_dict[data_set_name]["output_data_dir"] / "umap_embeddings.parquet"
    ).resolve()
    umap_embedding_df.to_parquet(umap_embeddings_file_path)
    print(f"UMAP embedding shape: {umap_embedding_df.shape}")
    umap_embedding_df.head()
    # scree plot analysis
    scree_pca.fit(features_df)
    pca_variance = scree_pca.explained_variance_ratio_

    scree_plot_file_path = pathlib.Path(
        input_data_dict[data_set_name]["output_data_dir"] / "scree_plot.parquet"
    ).resolve()
    scree_plot_df = pd.DataFrame(pca_variance, columns=["Explained Variance"])
    scree_plot_df["Principal Component"] = range(1, max_pca_components + 1)
    scree_plot_df.to_parquet(scree_plot_file_path)

    # perform PCA on the data

    pca_embedding = pca_reducer.fit_transform(features_df)
    pca_embedding_df = pd.DataFrame(pca_embedding, columns=["PCA0", "PCA1"])
    pca_embedding_df = pd.concat(
        [metadata_columns_df.reset_index(drop=True), pca_embedding_df], axis=1
    )

    pca_embeddings_file_path = pathlib.Path(
        input_data_dict[data_set_name]["output_data_dir"] / "pca_embeddings.parquet"
    ).resolve()
    pca_embedding_df.to_parquet(pca_embeddings_file_path)
    print(f"PCA embedding shape: {pca_embedding_df.shape}")
    pca_embedding_df.head()

