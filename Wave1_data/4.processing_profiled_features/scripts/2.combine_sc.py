#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import pathlib

import lancedb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pycytominer import annotate
from pycytominer.cyto_utils import output

# ## Set paths and variables

# In[2]:


# directory where parquet files are located
data_dir = pathlib.Path("../data/converted_data")

# directory where the annotated parquet files are saved to
data_dir = pathlib.Path("../data/annotated_data")

output_dir = pathlib.Path("../data/annotated_data_combined/")
output_dir.mkdir(exist_ok=True)
# get all the parquet files in the directory recursively
files = list(data_dir.glob("**/*.parquet"))
files = [file for file in files if file.is_file()]
print(f"Found {len(files)} files")


# This last cell does not get run due to memory constraints.
# It is run on an HPC cluster with more memory available.

# In[ ]:


# get a list of all files in the data directory
df = pd.concat([pd.read_parquet(file) for file in files])
print(df.shape)
df.to_parquet(output_dir / "live_cell_pyroptosis_wave1_sc.parquet")
df.head()
