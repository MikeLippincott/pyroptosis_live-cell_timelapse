#!/usr/bin/env python
# coding: utf-8

# This notebook explores the data at hand to understand the distribution and shape, as well as perform some pca and UMAP analysis to understand the data better.

# In[1]:


import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
import umap
from sklearn.decomposition import PCA

# In[2]:


figure_dir = pathlib.Path("../figures").resolve()
output_data_dir = pathlib.Path("../data").resolve()
figure_dir.mkdir(parents=True, exist_ok=True)
output_data_dir.mkdir(parents=True, exist_ok=True)

data_subset = True


# In[3]:


input_file_path_subset = pathlib.Path(
    "../../4.processing_profiled_features/data/preprocessed_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs_subset.parquet"
).resolve()
input_file_path = pathlib.Path(
    "../../4.processing_profiled_features/data/feature_selected_data/live_cell_pyroptosis_wave1_sc_first_time_norm_fs.parquet"
).resolve()
agg_file_path = pathlib.Path(
    "../../4.processing_profiled_features/data/aggregated/live_cell_pyroptosis_wave1_first_time_norm_fs_agg.parquet"
).resolve()
output_data_dir = pathlib.Path("../data/first_time").resolve()
figure_dir = pathlib.Path("../figures/first_time").resolve()


# In[4]:


random_state = 0
umap_reducer = umap.UMAP(
    n_neighbors=15, min_dist=0.1, n_components=2, random_state=random_state
)
max_pca_components = 100
scree_pca = PCA(n_components=max_pca_components)
pca_reducer = PCA(n_components=2, random_state=random_state)

if data_subset:
    data_df = pd.read_parquet(input_file_path_subset)
else:
    data_df = pd.read_parquet(input_file_path)
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
    output_data_dir / "umap_embeddings.parquet"
).resolve()
umap_embedding_df.to_parquet(umap_embeddings_file_path)
print(f"UMAP embedding shape: {umap_embedding_df.shape}")
umap_embedding_df.head()
# scree plot analysis
scree_pca.fit(features_df)
pca_variance = scree_pca.explained_variance_ratio_

scree_plot_file_path = pathlib.Path(output_data_dir / "scree_plot.parquet").resolve()
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
    output_data_dir / "pca_embeddings.parquet"
).resolve()
pca_embedding_df.to_parquet(pca_embeddings_file_path)
print(f"PCA embedding shape: {pca_embedding_df.shape}")
pca_embedding_df.head()


# ### Process agg

# In[5]:


umap_reducer = umap.UMAP(
    n_neighbors=15, min_dist=0.1, n_components=2, random_state=random_state
)
max_pca_components = 100
scree_pca = PCA(n_components=max_pca_components)
pca_reducer = PCA(n_components=2, random_state=random_state)

agg_df = pd.read_parquet(agg_file_path)
# set the UMAP parameters
# separate the data into features and labels
metadata_columns = agg_df.columns[agg_df.columns.str.contains("Metadata")]
metadata_columns_df = agg_df[metadata_columns]
features_df = agg_df.drop(metadata_columns, axis=1)
features_df = features_df.fillna(0)
print(
    f"Original data shape: {agg_df.shape}, features shape: {features_df.shape}, and metadata shape: {metadata_columns_df.shape}"
)

# fit the UMAP model
umap_embedding = umap_reducer.fit_transform(features_df)
umap_embedding_df = pd.DataFrame(umap_embedding, columns=["UMAP0", "UMAP1"])
umap_embedding_df = pd.concat(
    [metadata_columns_df.reset_index(drop=True), umap_embedding_df], axis=1
)
output_data_dir = pathlib.Path("../data/first_time").resolve()
umap_embeddings_file_path = pathlib.Path(
    output_data_dir / "aggregate_umap_embeddings.parquet"
).resolve()
umap_embedding_df.to_parquet(umap_embeddings_file_path)
print(f"UMAP embedding shape: {umap_embedding_df.shape}")
umap_embedding_df.head()
# scree plot analysis
scree_pca.fit(features_df)
pca_variance = scree_pca.explained_variance_ratio_

scree_plot_file_path = pathlib.Path(output_data_dir / "scree_plot.parquet").resolve()
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
    output_data_dir / "aggregate_pca_embeddings.parquet"
).resolve()
pca_embedding_df.to_parquet(pca_embeddings_file_path)
print(f"PCA embedding shape: {pca_embedding_df.shape}")
pca_embedding_df.head()
