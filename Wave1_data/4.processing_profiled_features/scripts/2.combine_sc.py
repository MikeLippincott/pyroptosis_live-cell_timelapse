#!/usr/bin/env python
# coding: utf-8

# # Annotate merged single cells with metadata from platemap file

# ## Import libraries

# In[1]:


import json
import pathlib
import sys

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


# In[3]:


# get a list of all files in the data directory
files = list(data_dir.glob("*.parquet"))
df = pd.concat([pd.read_parquet(file) for file in files])
print(df.shape)
df.to_parquet(output_dir / "live_cell_pyroptosis_wave1_sc.parquet")
df.head()

