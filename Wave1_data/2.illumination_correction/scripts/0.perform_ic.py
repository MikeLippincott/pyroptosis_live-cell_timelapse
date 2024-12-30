#!/usr/bin/env python
# coding: utf-8

# # Run CellProfiler `illum.cppipe` (IC) pipeline
#
# In this notebook, we run the CellProfiler IC pipeline to calculate the illumination (illum) correction functions for all images per channel (5), apply the functions, and save images into a new directory.

# ## Import libraries

# In[ ]:


import argparse
import pathlib
import sys
import time

sys.path.append("../../../utils")
import cp_parallel
import cp_utils as cp_utils
import tqdm

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False


# ## Set paths

# In[ ]:


if not in_notebook:
    print("Running as script")
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--input_dir",
        type=str,
        help="Path to the input directory containing the tiff images",
    )

    args = parser.parse_args()
    input_dir = pathlib.Path(args.input_dir).resolve(strict=True)
else:
    print("Running in a notebook")
    input_dir = pathlib.Path("../examples/raw_z_input/").resolve(strict=True)

run_name = "illumination_correction"
# path to folder for IC images
illum_directory = pathlib.Path("../illum_directory").resolve()
# make sure the directory exists
illum_directory.mkdir(exist_ok=True, parents=True)


# ## Define the input paths

# 5 FOVs per well, 96 wells per plate, 1 plate at 18 time points = 8640 image sets

# In[ ]:


path_to_pipeline = pathlib.Path("../pipelines/illum_5ch.cppipe").resolve(strict=True)
# get all directories with raw images
dict_of_runs = {}
input_directories = list(input_dir.rglob("*"))
input_directories = [x for x in input_directories if x.is_dir()]
# filter for directories with images
raw_directories = [x for x in input_directories if len(list(x.glob("*.tif"))) > 0]
raw_directories = sorted(raw_directories)

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
