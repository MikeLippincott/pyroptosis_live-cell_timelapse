#!/usr/bin/env python
# coding: utf-8

# # Normalize annotated single cells using negative control

# ## Import libraries

# In[ ]:


import os
import pathlib

import pandas as pd
from pycytominer import normalize
from pycytominer.cyto_utils import output
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


# ## Set paths and variables

# In[ ]:


if in_notebook:
    import tqdm.notebook as tqdm

    plate_name = "plate_2"
else:
    import tqdm

    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    plate_name = args.plate_name


# In[ ]:


# load in platemap file as a pandas dataframe
platemap_path = pathlib.Path(
    f"{root_dir}/Wave2_data/0.download_data/platemap/platemap.csv"
).resolve()

image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
sc_tracks_path = pathlib.Path(
    f"{image_base_dir}/9.single_Cell_tracks_merged/{plate_name}/sc_tracks_profiles.parquet"
).resolve(strict=True)

normalized_profiles_path = pathlib.Path(
    f"{image_base_dir}/10.normalized_profiles/{plate_name}/normalized_profiles.parquet"
).resolve()
normalized_profiles_path.parent.mkdir(exist_ok=True)


# ## Normalize with standardize method with negative control on annotated data

# The normalization needs to occur per time step.
# This code cell will split the data into time steps and normalize each time step separately.
# Then each normalized time step will be concatenated back together.

# This last cell does not get run due to memory constraints.
# It is run on an HPC cluster with more memory available.

# In[5]:


# set the metadata conditions to fit and apply normalization to
samples = "Metadata_Inducer == 'DMSO' & Metadata_Inducer_dose == '0.15%' & Metadata_Inhibitor == 'DMSO' & Metadata_Inhibitor_dose == '0.15%' & Metadata_Time == '1'"


# In[ ]:


# read in the annotated file
annotated_df = pd.read_parquet(sc_tracks_path)
# get the features (not the metadata) to use for normalization
features = [col for col in annotated_df.columns if "metadata" not in col.lower()]
# apply normalization to the annotated df using the specified samples as the reference for normalization
normalized_df = normalize(
    # df with annotated raw merged single cell features
    profiles=annotated_df,
    features=features,
    # specify samples used as normalization reference (negative control)
    samples=samples,
    # normalization method used
    method="standardize",
)
# save the normalized profiles as a parquet file
output(
    normalized_df,
    output_filename=normalized_profiles_path,
    output_type="parquet",
)
if annotated_df.shape[0] != normalized_df.shape[0]:
    raise ValueError(
        f"Number of rows in the annotated df ({annotated_df.shape[0]}) does not match the number of rows in the normalized df ({normalized_df.shape[0]}). Please check the input annotated df and the samples used for normalization."
    )
normalized_df.head()
