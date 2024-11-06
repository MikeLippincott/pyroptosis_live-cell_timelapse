#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=06:00:00
#SBATCH --output=parent-%j.out

# this script submits the jobs to the cluster to run the pipeline
# note that the jobs are submitted in the order of the pipeline
# we have to wait for the previous job to finish before submitting the next job
conda init bash

cd 2.illumination_correction || exit
# check if output folder exists
if [ -e "./illum_directory" ]; then
    rm -r ./illum_directory
fi

job1=$(sbatch run_ic.sh --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=../ic-%j.out | cut -f 4 -d " ")

cd ../3.cellprofiling || exit
if [ -e "./analysis_output" ]; then
    rm -r ./analysis_output
fi
job2=$(sbatch perform_cellprofiling.sh --dependency=afterok:$job1 --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=../cp-%j.out | cut -f 4 -d " ")

cd ../4.processing_profiled_features || exit
if [ -e "./data" ]; then
    rm -r ./data
fi

sbatch run_processing.sh --dependency=afterok:$job2 --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=../process_cp-%j.out
source process_cellprofiling.sh

cd .. || exit

echo "All done"
