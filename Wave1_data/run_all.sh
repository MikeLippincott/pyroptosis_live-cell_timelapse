#!/bin/bash

# this script submits the jobs to the cluster to run the pipeline
# note that the jobs are submitted in the order of the pipeline
# we have to wait for the previous job to finish before submitting the next job

cd 2.illumination_correction || exit
# check if output folder exists
if [ -e "./illum_directory" ]; then
    rm -r ./illum_directory
fi

source run_illum.sh

cd ../3.cellprofiling || exit
if [ -e "./analysis_output" ]; then
    rm -r ./analysis_output
fi

source run_cellprofiling.sh

cd ../4.processing_pofiled_features || exit
if [ -e "./data" ]; then
    rm -r ./data
fi

source process_cellprofiling.sh

cd .. || exit

echo "All done"
