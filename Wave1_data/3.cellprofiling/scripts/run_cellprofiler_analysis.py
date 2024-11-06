#!/usr/bin/env python
# coding: utf-8

# # Perform segmentation and feature extraction for each plate using CellProfiler Parallel

# ## Import libraries

# In[1]:


import pathlib
import pprint
import sys
import time

sys.path.append("../../../utils/")
import cp_parallel


# ## Set paths and variables

# In[2]:


# set the run type for the parallelization
run_name = "analysis"

# set main output dir for all plates
output_dir = pathlib.Path("../analysis_output")
output_dir.mkdir(exist_ok=True, parents=True)

# directory where images are located within folders
images_dir = pathlib.Path("../../2.illumination_correction/illum_directory/")

# path to plugins directory as one of the pipelines uses the RunCellpose plugin
plugins_dir = pathlib.Path(
    "/home/lippincm/Documents/CellProfiler-plugins/active_plugins"
)
path_to_pipeline = pathlib.Path("../pipelines/analysis_5ch.cppipe").resolve(strict=True)


# ## Create dictionary with all info for each well

# In[3]:


# get all directories with raw images
dict_of_runs = {}
raw_directories = list(images_dir.rglob("*"))
raw_directories = [x for x in raw_directories if x.is_dir()]
# filter for directories with images
raw_directories = [x for x in raw_directories if len(list(x.glob("*.tiff"))) > 0]
# #####################################
# # for testing purposes
# raw_directories = raw_directories[:2]
# #####################################

for dir in raw_directories:
    dict_of_runs[dir.name] = {
        "path_to_images": str(dir),
        "path_to_output": str(pathlib.Path(output_dir / dir.name)),
        "path_to_pipeline": str(path_to_pipeline),
    }
print("Number of directories to process: ", len(dict_of_runs))


# ## Run analysis pipeline on each plate in parallel
# 
# This cell is not finished to completion due to how long it would take. It is ran in the python file instead.

# In[4]:


start = time.time()


# In[5]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=dict_of_runs,
    run_name=run_name,
    #plugins_dir=plugins_dir,
)


# In[6]:


end = time.time()
# format the time taken into hours, minutes, seconds
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
print(
    "Total time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
)

