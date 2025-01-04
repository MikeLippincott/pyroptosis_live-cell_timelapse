# Illumination Correction
This module is used to perform illumination correction on all microscopy images.
This is done by using a CellProfiler pipeline that is run on all images in the dataset.

For for information about the data please see the [Wave 1 Data README](../README.md).

Here we use High Performance Computing (HPC) to run the CellProfiler pipeline on all images in the dataset.
We use a parent script to call and submit the child scripts to the HPC.
On a slurm system (like the one we use) the parent script will submit a job for each child script.
