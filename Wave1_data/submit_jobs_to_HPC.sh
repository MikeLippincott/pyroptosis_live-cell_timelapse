#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=06:00:00
#SBATCH --output=parent-%j.out
#SBATCH --dependency=afterok:job1:job2:job3

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

job1=$(sbatch run_ic.sh --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=ic-%j.out | cut -f 4 -d " ")

cd ../3.cellprofiling || exit
if [ -e "./analysis_output" ]; then
    rm -r ./analysis_output
fi
job2=$(sbatch perform_cellprofiling.sh --dependency=afterok:$job1 --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=cp-%j.out | cut -f 4 -d " ")

cd ../4.processing_profiled_features || exit
if [ -e "./data" ]; then
    rm -r ./data
fi

job3=$(sbatch process_cellprofiling.sh --dependency=afterok:$job2 --ntasks=8 --time=00:60:00 --partition=amilan --qos=normal --account=amc-general --output=process_cp-%j.out | cut -f 4 -d " ")

cd .. || exit

# move the slurm outputs to this dir
mv 2.illumination_correction/slurm* .
mv 3.cellprofiling/slurm* .
mv 4.processing_profiled_features/slurm* .

echo "All done"
