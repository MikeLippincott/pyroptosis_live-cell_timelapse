#!/usr/bin/env python
# coding: utf-8

# # Merge single cells from CellProfiler outputs using CytoTable

# In[1]:


import argparse
import multiprocessing
import os
import pathlib
import time
import uuid

import natsort
import pandas as pd
from cytotable import convert, presets
from timelapse_utils.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm

from parsl.config import Config
from parsl.executors import HighThroughputExecutor

# In[8]:


def process_single_file(args):
    """
    Process a single well_fov_timepoint sqlite file.
    Returns a result dict with status, timing, and error info.
    """
    well_fov_timepoint_sqlite_file_path, output_dir, dest_datatype, preset = args

    well_fov_timepoint = well_fov_timepoint_sqlite_file_path.stem
    dest_path = output_dir / well_fov_timepoint
    dest_path.mkdir(exist_ok=True, parents=True)
    dest_path = dest_path / f"{well_fov_timepoint}.{dest_datatype}"

    # Skip if already exists
    if dest_path.exists():
        return {"status": "exists", "well_fov_timepoint": well_fov_timepoint}

    # Extract metadata from filename
    parts = well_fov_timepoint.split("_")
    well = parts[0]
    fov = parts[1]
    timepoint = int(parts[2].strip("T"))

    try:
        start_time = time.time()

        convert(
            source_path=well_fov_timepoint_sqlite_file_path,
            dest_path=dest_path,
            dest_datatype=dest_datatype,
            preset=preset,
            parsl_config=Config(
                executors=[HighThroughputExecutor()],
                run_dir=f"cytotable_runinfo/{uuid.uuid4().hex}",
            ),
            chunk_size=1000,
        )

    except Exception as e:
        return {
            "status": "error",
            "well_fov_timepoint": well_fov_timepoint,
            "error": str(e),
        }

    # Read and clean the parquet output
    df = pd.read_parquet(dest_path)

    df.drop(
        columns=[
            "Metadata_ImageNumber_1",
            "Metadata_ImageNumber_2",
            "Metadata_ImageNumber_3",
        ],
        inplace=True,
    )

    location_metadata = [
        x
        for x in df.columns
        if "center_" in x.lower()
        or "location" in x.lower()
        or "boundingbox" in x.lower()
    ]

    file_metadata = [
        "Image_URL_BF",
        "Image_URL_CL488",
        "Image_URL_CL640",
        "Image_URL_NucleoLive",
        "Image_URL_SYTOXGreen",
    ]

    object_metadata = [
        x
        for x in df.columns
        if "count" in x.lower()
        or ("parent" in x.lower() and "metadata" not in x.lower())
    ]

    df.rename(
        columns={
            x: f"Metadata_{x}"
            for x in file_metadata + object_metadata + location_metadata
            if "Metadata" not in x
        },
        inplace=True,
    )

    df.insert(0, "Metadata_Well", well)
    df.insert(1, "Metadata_Time", timepoint)
    df.insert(2, "Metadata_FOV", fov)
    df.insert(2, "Metadata_Well_FOV", df["Metadata_Well"] + "_" + df["Metadata_FOV"])
    df.insert(
        4,
        "Metadata_Well_FOV_Time",
        df["Metadata_Well_FOV"] + "_" + df["Metadata_Time"].astype(str),
    )
    df["Metadata_single_cell_count"] = df.shape[0]
    df.to_parquet(dest_path)

    end_time = time.time()

    return {
        "status": "success",
        "well_fov_timepoint": well_fov_timepoint,
        "time": end_time - start_time,
    }


def process_all_files(
    well_fov_timepoints_sqlites,
    output_dir,
    dest_datatype,
    preset,
    n_workers=None,  # Defaults to os.cpu_count()
):
    """
    Parallelized version of the file processing loop.
    """
    times_dict = {"well_fov_timepoint": [], "time": []}
    exists = 0
    total = 0
    errors_counter = 0
    errors = []

    if n_workers is None:
        n_workers = 1
    # Build args list for starmap
    args_list = [
        (path, output_dir, dest_datatype, preset)
        for path in well_fov_timepoints_sqlites
    ]
    total = len(args_list)

    with multiprocessing.Pool(processes=n_workers) as pool:
        results = list(
            tqdm.tqdm(
                pool.imap_unordered(process_single_file, args_list),
                total=total,
            )
        )

    # Aggregate results
    for result in results:
        if result["status"] == "exists":
            exists += 1
        elif result["status"] == "error":
            errors_counter += 1
            errors.append((result["well_fov_timepoint"], result["error"]))
        elif result["status"] == "success":
            times_dict["well_fov_timepoint"].append(result["well_fov_timepoint"])
            times_dict["time"].append(result["time"])

    print(f"Total: {total}, Exists: {exists}, Errors: {errors_counter}")
    for well_fov_timepoint, error in errors:
        print(f"Error processing {well_fov_timepoint}: {error}")

    return times_dict


# ## set config joins for each preset

# In[9]:


# preset configurations based on typical CellProfiler outputs
preset = "cellprofiler_sqlite_pycytominer"
presets.config[preset][
    "CONFIG_JOINS"
    # remove Image_Metadata_Plate from SELECT as this metadata was not extracted from file names
    # add Image_Metadata_FOV as this is an important metadata when finding where single cells are located
] = """WITH Per_Image_Filtered AS (
                SELECT
                    Metadata_ImageNumber,
                    Image_URL_CL488,
                    Image_URL_CL640,
                    Image_URL_NucleoLive,
                    Image_URL_BF,
                    Image_URL_SYTOXGreen,
                FROM
                    read_parquet('per_image.parquet')
                )
            SELECT
                *
            FROM
                Per_Image_Filtered AS per_image
            LEFT JOIN read_parquet('per_cytoplasm.parquet') AS per_cytoplasm ON
                per_cytoplasm.Metadata_ImageNumber = per_image.Metadata_ImageNumber
            LEFT JOIN read_parquet('per_cells.parquet') AS per_cells ON
                per_cells.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_cells.Metadata_Cells_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Cells
            LEFT JOIN read_parquet('per_nuclei.parquet') AS per_nuclei ON
                per_nuclei.Metadata_ImageNumber = per_cytoplasm.Metadata_ImageNumber
                AND per_nuclei.Metadata_Nuclei_Number_Object_Number = per_cytoplasm.Metadata_Cytoplasm_Parent_Nuclei
            """


# ## Set paths and variables
#
# All paths must be string but we use pathlib to show which variables are paths

# In[ ]:


if not in_notebook:
    argparser = argparse.ArgumentParser(description="Run feature merging")
    argparser.add_argument(
        "--well_fov",
        type=str,
        help="The well and fov to process in the format 'well_fov' (e.g., 'A01_01')",
    )
    argparser.add_argument(
        "--max_workers",
        type=int,
        default=4,
        help="The maximum number of workers to use for parallel processing",
    )
    argparser.add_argument(
        "--plate_name",
        type=str,
        help="Name of the plate to analyze",
    )
    args = argparser.parse_args()
    well_fov = args.well_fov
    max_workers = args.max_workers
    plate_name = args.plate_name
else:  # example input for notebook testing
    well_fov = "O2_2"
    max_workers = 4

well, fov = well_fov.split("_")


image_base_dir = bandicoot_check(
    bandicoot_mount_path=pathlib.Path(f"{os.path.expanduser('~')}/mnt/bandicoot/"),
    root_dir=root_dir,
)
image_base_dir = pathlib.Path(f"{image_base_dir}/processed_data/").resolve(strict=True)
extracted_features_dir = pathlib.Path(
    f"{image_base_dir}/4.extracted_features/{plate_name}"
).resolve(strict=True)


# In[ ]:


# type of file output from CytoTable (currently only parquet)
dest_datatype = "parquet"

# directory where parquet files are saved to
output_dir = pathlib.Path(
    f"{image_base_dir}/5.converted_profiles/{plate_name}"
).resolve()
output_dir.mkdir(exist_ok=True, parents=True)


# ## Gather all sqlite files for each well_fov_timepoint

# In[22]:


# well_fov_timepoints
well_fov_timepoints = [
    x for x in tqdm.tqdm(extracted_features_dir.glob(f"*{well_fov}*")) if x.is_dir()
]
well_fov_timepoints = natsort.natsorted(well_fov_timepoints)
well_fov_timepoints_sqlites = [
    list(x.glob("**/*.sqlite"))[0]
    for x in tqdm.tqdm(
        well_fov_timepoints,
        desc="Finding sqlite files for each well_fov_timepoint...",
        total=len(well_fov_timepoints),
    )
    if len(list(x.glob("**/*.sqlite"))) > 0
]
well_fov_timepoints_sqlites = natsort.natsorted(well_fov_timepoints_sqlites)


# ## Convert SQLite file and merge single cell objects into parquet file
#
# This was not run to completion as we use the nbconverted python file for full run.

# In[23]:


process_all_files(
    well_fov_timepoints_sqlites=well_fov_timepoints_sqlites,
    output_dir=output_dir,
    dest_datatype=dest_datatype,
    preset=preset,
    n_workers=max_workers,
)


# In[ ]:
