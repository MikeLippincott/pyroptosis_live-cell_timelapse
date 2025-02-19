#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, Image, display
from matplotlib import animation

# In[2]:


input_data_dict = {
    "first_time": {
        "umap_file_path": pathlib.Path(
            "../data/first_time/umap_embeddings.parquet"
        ).resolve(strict=True),
        "figure_dir": pathlib.Path("../figures/first_time/timelapse_gifs").resolve(),
    },
}
pprint(input_data_dict)

visualize = False


# In[ ]:


for profile in input_data_dict.keys():
    # make figure directory if it does not exist
    output_path = input_data_dict[profile]["figure_dir"]
    output_path.mkdir(parents=True, exist_ok=True)
    # read in the umap embeddings
    umap_df = pd.read_parquet(input_data_dict[profile]["umap_file_path"])
    print(umap_df.shape)
    # define an interval for the animation
    # I want it to be 5 frames per second (fps)
    # so I will set the interval to 1000/5
    fps = 5
    interval = 1000 / fps
    print(f"Interval: {interval}")

    for treatment in umap_df["Metadata_treatment"].unique():
        treatment_name = treatment.replace(" ", "_").replace("/", "_")
        tmp_df = umap_df.loc[umap_df["Metadata_treatment"] == treatment]
        classes = umap_df["Metadata_Time"].unique()
        # split the data into n different dfs based on the classes
        dfs = [tmp_df[tmp_df["Metadata_Time"] == c] for c in classes]
        for i in range(len(dfs)):
            df = dfs[i]
            # split the data into the Metadata and the Features
            metadata_columns = df.columns[df.columns.str.contains("Metadata")]
            metadata_df = df[metadata_columns]
            features_df = df.drop(metadata_columns, axis=1)
            dfs[i] = features_df

        # plot the list of dfs and animate them
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-6, 5)
        ax.set_ylim(-3, 10)
        scat = ax.scatter([], [], c="b", s=0.1)
        text = ax.text(-9, -9, "", ha="left", va="top")
        # add title
        ax.set_title(f"{treatment}")
        # axis titles
        ax.set_xlabel("UMAP0")
        ax.set_ylabel("UMAP1")

        def animate(i):
            df = dfs[i]
            i = i * 30
            scat.set_offsets(df.values)
            text.set_text(f"{i} minutes.")
            return (scat,)

        anim = animation.FuncAnimation(
            fig, init_func=None, func=animate, frames=len(dfs), interval=interval
        )
        anim.save(f"{output_path}/{treatment_name}.gif", writer="imagemagick")
        plt.close(fig)

        if visualize:
            # Display the animations
            for treatment in umap_df["Metadata_treatment"].unique():
                treatment_name = treatment.replace(" ", "_").replace("/", "_")
                with open(f"{output_path}/test_{treatment_name}.gif", "rb") as f:
                    display(Image(f.read()))
