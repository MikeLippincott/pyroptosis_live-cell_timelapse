#!/usr/bin/env python
# coding: utf-8

# # Run CellProfiler `illum.cppipe` (IC) pipeline
# 
# In this notebook, we run the CellProfiler IC pipeline to calculate the illumination (illum) correction functions for all images per channel (5), apply the functions, and save images into a new directory.

# ## Import libraries

# In[1]:


import pathlib
import sys
import time

sys.path.append("../../../utils")
import cp_parallel
import cp_utils as cp_utils
import tqdm


# ## Set paths

# In[2]:


run_name = "illumination_correction"
# path to folder for IC images
illum_directory = pathlib.Path("../illum_directory").resolve()
# make sure the directory exists
illum_directory.mkdir(exist_ok=True, parents=True)


# ## Define the input paths

# 5 FOVs per well, 96 wells per plate, 1 plate at 18 time points = 8640 image sets

# In[4]:


path_to_pipeline = pathlib.Path("../pipelines/illum_5ch.cppipe").resolve(strict=True)
raw_images_path = pathlib.Path("../../../data/raw").resolve(strict=True)
# get all directories with raw images
dict_of_runs = {}
raw_directories = list(raw_images_path.rglob("*"))
raw_directories = [x for x in raw_directories if x.is_dir()]
# filter for directories with images
raw_directories = [x for x in raw_directories if len(list(x.glob("*.tif"))) > 0]
raw_directories = sorted(raw_directories)
#####################################
# for testing purposes
# get 5 random directories with images
import random

import numpy as np

random.seed(0)
DMSO_sample = raw_directories[5:20]
raw_directories = random.sample(raw_directories, 2)
raw_directories = DMSO_sample + raw_directories
#####################################
for dir in raw_directories:
    well_FOV = dir.name
    plate = str(dir).split("/")[-2]
    plate_well_FOV = plate + well_FOV
    dict_of_runs[plate_well_FOV] = {
        "path_to_images": dir,
        "path_to_output": illum_directory / plate_well_FOV,
        "path_to_pipeline": path_to_pipeline,
    }
print(f"Added {len(dict_of_runs.keys())} to the list of runs")


# ## Run `illum.cppipe` pipeline and calculate + save IC images
# This last cell does not get run as we run this pipeline in the command line.

# In[ ]:


start = time.time()


# In[ ]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=dict_of_runs, run_name=run_name
)


# In[ ]:


end = time.time()
# format the time taken into hours, minutes, seconds
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
print(
    "Total time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
)

