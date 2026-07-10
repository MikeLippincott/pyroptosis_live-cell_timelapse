#!/usr/bin/env python
# coding: utf-8

# # Perform segmentation and feature extraction for each plate using CellProfiler Parallel

# ## Import libraries

# In[ ]:


import argparse
import os
import pathlib
import pprint
import shutil
import time

from timelapse_utils.cp_utils.cp_parallel import run_cellprofiler_parallel
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()


image_based_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)


# In[ ]:


if in_notebook:
    import tqdm.notebook as tqdm

    max_workers = 2
    plate_name = "plate_1"
else:
    import tqdm

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--max_workers",
        type=int,
        default=None,
        help="The maximum number of workers to use for parallel processing. If not specified, the number of workers will be set to the number of CPU cores minus 2.",
    )
    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    max_workers = args.max_workers
    plate_name = args.plate_name


# ## Set paths and variables

# In[ ]:


path_to_pipeline = pathlib.Path(
    f"{root_dir}/Wave2_data/5.feature_extraction/pipelines/analysis_5ch.cppipe"
).resolve(strict=True)
load_file_dir = pathlib.Path(f"{root_dir}/Wave2_data/5.feature_extraction/loadfiles/")


# In[ ]:


# find all dirs in loadfiles path that contain the well_fov name (one per timepoint)
timepoint_dirs = sorted(load_file_dir.glob(f"*/*"))


# ## Create dictionary with all info for each well

# In[ ]:


# get all directories with raw images
dict_of_runs = {}
for timepoint_dir in tqdm.tqdm(timepoint_dirs):
    dict_of_runs[timepoint_dir.name] = {
        "path_to_images": str(timepoint_dir),
        "path_to_output": str(
            pathlib.Path(
                f"{root_dir}/Wave2_data/5.feature_extraction/extracted_features/{plate_name}/{timepoint_dir.name}"
            ).resolve()
        ),
        "path_to_final_output": str(
            pathlib.Path(
                f"{image_based_dir}/processed_data/3.extracted_features/{plate_name}/{timepoint_dir.name}"
            ).resolve()
        ),
        "path_to_pipeline": path_to_pipeline,
    }
    pathlib.Path(dict_of_runs[timepoint_dir.name]["path_to_output"]).mkdir(
        exist_ok=True, parents=True
    )
    pathlib.Path(dict_of_runs[timepoint_dir.name]["path_to_final_output"]).mkdir(
        exist_ok=True, parents=True
    )
    # check if there is a file in the final output dir
    # if so then remove this timepoint from the dict of runs
    if (
        len(
            list(
                pathlib.Path(
                    dict_of_runs[timepoint_dir.name]["path_to_final_output"]
                ).glob("*")
            )
        )
        > 0
    ):
        # remove this record from the run dict
        dict_of_runs.pop(timepoint_dir.name, None)
print(f"Found {len(dict_of_runs.keys())} timepoints to run CellProfiler on.")
if len(dict_of_runs.keys()) < 100:
    pprint.pprint(dict_of_runs)


# ## Run analysis pipeline on each plate in parallel
#
# This cell is not finished to completion due to how long it would take. It is ran in the python file instead.

# In[ ]:


try:
    path_to_apptainer_image = pathlib.Path(
        f"{root_dir}/environments/cellprofiler.sif"
    ).resolve(strict=True)
    print(path_to_apptainer_image)
    print("Using apptainer image for CellProfiler run.")
except FileNotFoundError:
    print("No apptainer image found, running CellProfiler without apptainer.")
    path_to_apptainer_image = None


# ## This section gets run in script only as it takes a long time to run. It is not ran in the notebook.

# In[ ]:


# run CellProfiler in batches so local storage can be cleared between runs
# we need to run locally first for three reasons
# 1 latency
# 2 write permissions on the NAS do not permit to update serial files
# 3 we do not have the local storage available for all of these CP SQlites
batch_size = 96
dict_of_runs_items = list(dict_of_runs.items())
start = time.time()

for batch_start in range(0, len(dict_of_runs_items), batch_size):
    batch_dict_of_runs = dict(
        dict_of_runs_items[batch_start : batch_start + batch_size]
    )
    print(
        f"Running CellProfiler batch {batch_start // batch_size + 1} ",
        f"with {len(batch_dict_of_runs)} timepoints.",
    )
    run_cellprofiler_parallel(
        plate_info_dictionary=batch_dict_of_runs,
        run_name="timelapse_pyroptosis_wave2_analysis",
        run_with_apptainer_interactive=path_to_apptainer_image,
        log_dir=pathlib.Path(
            f"{root_dir}/Wave2_data/5.feature_extraction/logs/"
        ).resolve(),
        max_workers=max_workers,
    )

    # loop through the dict of runs and move the output files to the final output directory
    # the final output file is on a NAS and cellprofiler cannot update the write file in place, so we need to move the file to the final output directory
    for well_fov_timepoint in batch_dict_of_runs.keys():
        tmp_output_file_path = pathlib.Path(
            f"{batch_dict_of_runs[well_fov_timepoint]['path_to_output']}/pyroptosis_timelapse.sqlite"
        )
        final_output_file_path = pathlib.Path(
            f"{batch_dict_of_runs[well_fov_timepoint]['path_to_final_output']}/{well_fov_timepoint}.sqlite"
        )
        if not tmp_output_file_path.exists():
            continue
        final_output_file_path.parent.mkdir(parents=True, exist_ok=True)
        # check to make sure the final output is not the same as the tmp output file
        # (this can happen if the final output dir is on a local drive
        # and the tmp output dir is on a NAS)
        if tmp_output_file_path.resolve() == final_output_file_path.resolve():
            continue
        if final_output_file_path.exists():
            final_output_file_path.unlink()
        # use move (copy+remove fallback) to support cross-device paths
        shutil.move(str(tmp_output_file_path), str(final_output_file_path))

end = time.time()
# format the time taken into hours, minutes, seconds
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
print(
    "Total time taken: {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(minutes), seconds
    ),
)
