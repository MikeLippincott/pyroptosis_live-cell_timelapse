#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib

import pandas as pd

# In[2]:


file_paths = pathlib.Path("../results_of_memory_profiling").resolve().glob("*")
output_file_path = pathlib.Path(
    "../results_of_memory_profiling/concatenated_results.parquet"
).resolve()
file_paths = sorted(file_paths)


# In[3]:


list_of_dfs = [
    pd.read_parquet(file_path)
    for file_path in file_paths
    if not file_path == output_file_path
]
concated_df = pd.concat(list_of_dfs, ignore_index=True)
concated_df.to_parquet(output_file_path)
concated_df.head()


# In[4]:


concated_df["total_MB"].max()
