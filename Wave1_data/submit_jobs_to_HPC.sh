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
module purge
module load anaconda
conda init bash

cd 2.illumination_correction || exit
# check if output folder exists
if [ -e "./illum_directory" ]; then
    rm -r ./illum_directory
fi

job1=$(sbatch run_ic.sh)
job1=${job1##*}

cd ../3.cellprofiling || exit
if [ -e "./analysis_output" ]; then
    rm -r ./analysis_output
fi
job2=$(sbatch perform_cellprofiling.sh --dependency=afterok:$job1)
job2=${job2##*}
cd ../4.processing_profiled_features || exit
if [ -e "./data" ]; then
    rm -r ./data
fi

job3=$(sbatch process_cellprofiling.sh --dependency=afterok:$job1:$job2 | cut -f 4 -d " ")

cd .. || exit

# move the slurm outputs to this dir

echo "All done"
