#!/usr/bin/env python
# coding: utf-8

# # Run CellProfiler `illum.cppipe` (IC) pipeline
# 
# In this notebook, we run the CellProfiler IC pipeline to calculate the illumination (illum) correction functions for all images per channel (5), apply the functions, and save images into a new directory.

# ## Import libraries

# In[1]:


import argparse
import pathlib
import sys
import time

sys.path.append("../../../utils")
import cp_utils
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
    input_dir = pathlib.Path("../../../data/test_dir/W0052_F0001").resolve(strict=True)

run_name = "illumination_correction"
# path to folder for IC images
illum_directory = pathlib.Path("../illum_directory").resolve()
# make sure the directory exists
illum_directory.mkdir(exist_ok=True, parents=True)


# ## Define the input paths

# 5 FOVs per well, 96 wells per plate, 1 plate at 18 time points = 8640 image sets

# In[9]:


path_to_pipeline = pathlib.Path("../pipelines/illum_5ch.cppipe").resolve(strict=True)
# get all directories with raw images


dict_of_runs = {}
dict_of_runs[input_dir.stem] = {
    "path_to_images": str(input_dir),
    "path_to_output": str(illum_directory / input_dir.stem),
    "path_to_pipeline": path_to_pipeline,
}
print(f"Added {len(dict_of_runs.keys())} to the list of runs")
print(f"Running {input_dir.stem}")


# ## Run `illum.cppipe` pipeline and calculate + save IC images
# This last cell does not get run as we run this pipeline in the command line.

# In[10]:


start = time.time()


# In[ ]:


cp_utils.run_cellprofiler(
    path_to_pipeline=dict_of_runs[input_dir.stem]["path_to_pipeline"],
    path_to_input=dict_of_runs[input_dir.stem]["path_to_images"],
    path_to_output=dict_of_runs[input_dir.stem]["path_to_output"],
)


# In[ ]:


end = time.time()
# format the time taken into hours, minutes, seconds
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
print(
    "Total time taken: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
)

