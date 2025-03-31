#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib

import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

# In[2]:


input_file_path = pathlib.Path(
    "../results_of_memory_profiling/concatenated_results.parquet"
).resolve(strict=True)
df = pd.read_parquet(input_file_path)
df.head()


# In[3]:


df["total_GB"] = df["total_MB"] / 1024
df["elapsed_time_minutes"] = df["elapsed_time"] / 60
df["total_cell_count"] = df["num_of_cells_per_well"] * df["num_of_wells"]
# make a column that is a tuple of the two columns
df["profile_shape"] = (
    df["num_of_features"].astype(str) + "_" + df["total_cell_count"].astype(str)
)
df.head()


# In[4]:


# 3d plot of the data

fig = plt.figure()
fig.set_size_inches(10, 10)
ax = fig.add_subplot(111, projection="3d")
ax.scatter(
    data=df,
    xs="num_of_features",
    ys="num_of_cells_per_well",
    zs="num_of_wells",
    c="total_GB",
    cmap="rainbow",
)


ax.set_xlabel("Feature number")
ax.set_ylabel("Cells per well")
ax.set_zlabel("Well number")
# add color bar
cbar = plt.colorbar(
    ax.collections[0],
    ax=ax,
    orientation="vertical",
    location="right",
    shrink=0.5,
    aspect=10,
    pad=0.25,
)
cbar.set_label("Total GB")

plt.title(
    "Memory usage as a function of the number of features, cells per well, and wells"
)

plt.show()


# In[5]:


# 3d plot of the data
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
fig.set_size_inches(10, 10)
ax = fig.add_subplot(111, projection="3d")
ax.scatter(
    data=df,
    xs="num_of_features",
    ys="num_of_cells_per_well",
    zs="num_of_wells",
    c="elapsed_time_minutes",
    cmap="rainbow",
)


ax.set_xlabel("Feature number")
ax.set_ylabel("Cells per well")
ax.set_zlabel("Well number")
# add color bar
cbar = plt.colorbar(
    ax.collections[0],
    ax=ax,
    orientation="vertical",
    location="right",
    shrink=0.5,
    aspect=10,
    pad=0.25,
)
cbar.set_label("Total Time (minutes)")
plt.title(
    "Elapsed time as a function of the number of features, cells per well, and wells"
)


plt.show()


# In[6]:


# 3d plot of the data
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
fig.set_size_inches(10, 10)
ax = fig.add_subplot(111, projection="3d")
ax.scatter(
    data=df,
    xs="num_of_features",
    ys="total_cell_count",
    zs="total_GB",
    c="elapsed_time_minutes",
    cmap="rainbow",
)


ax.set_xlabel("Feature number")
ax.set_ylabel("Total cell count")
ax.set_zlabel("Total GB")
# add color bar
cbar = plt.colorbar(
    ax.collections[0],
    ax=ax,
    orientation="vertical",
    location="right",
    shrink=0.5,
    aspect=10,
    pad=0.25,
)
cbar.set_label("Total Time (minutes)")
plt.title(
    "Elapsed time as a function of the number of features, cells per well, and wells"
)


plt.show()
