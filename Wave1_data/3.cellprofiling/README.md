# Cell Profiling Project

## Overview

This project is designed to perform cell profiling using CellProfiler. It includes Jupyter notebooks and shell scripts to automate the process of running CellProfiler analysis on a set of images.

## Directory Structure
Within the `3.cellprofiling` directory, you'll find the following files:
- `./notebooks/run_cellprofiler_analysis.ipynb`: Jupyter notebook for running CellProfiler analysis.
- `./perform_cellprofiling_parent.sh`: Shell script to submit multiple CellProfiler jobs to a SLURM cluster.
- `./perform_cellprofiling_child.sh`: Shell script to run a single CellProfiler job.

## Usage

### Running CellProfiler Analysis (Jupyter Notebook)

The Jupyter notebook `run_cellprofiler_analysis.ipynb` is used to run CellProfiler analysis on a set of images. It includes the following steps:

### Submitting CellProfiler Jobs to SLURM (Shell Scripts)

The shell scripts `perform_cellprofiling_parent.sh` and `perform_cellprofiling_child.sh` are used to submit and run CellProfiler jobs on a SLURM cluster.

`perform_cellprofiling_parent.sh`

This script submits multiple CellProfiler jobs to the SLURM cluster. It performs the following steps:

1. Converts Jupyter notebooks to Python scripts.
2. Gets a list of directories containing the raw data.
3. Submits a SLURM job for each directory using `sbatch`.

To run the script:

```sh
sbatch perform_cellprofiling_parent.sh
```
