#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=4:00:00
#SBATCH --output=annotate_sc_parent-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

# get the directory names of the well_fovs
mapfile -t well_fovs < <(ls -d ../data/converted_data/*)
cd ../ || exit
# array of well_fovs jobs
job_ids=()
for well_fov in "${well_fovs[@]}"; do
    number_of_jobs=$(squeue -u $USER | wc -l)
    while [ $number_of_jobs -gt 990 ]; do
        sleep 1s
        number_of_jobs=$(squeue -u $USER | wc -l)
    done
    job_id=$(sbatch 1.annotate_sc_child.sh "$well_fov" | cut -f 4 -d " ")
    job_ids+=("$job_id")
done


# check that all jobs have completed
running_total=0
completed_total=0
while [ $running_total -gt 1 ]; do
    running_total=0
    completed_total=0
    for job_id in "${job_ids[@]}"; do
        job_state=$(scontrol show job $job_id | grep "JobState" | cut -f 2 -d "=" | tr -d " ")
        if [ $job_state == "RUNNING" ]; then
            running_total=$((running_total+1))
        elif [ $job_state == "COMPLETED" ]; then
            completed_total=$((completed_total+1))
        fi
    done
    echo "Running jobs: $running_total"
    echo "Completed jobs: $completed_total"
    sleep 1s
done



# deactivate cellprofiler environment
conda deactivate

echo "Annotate sc processing completed."
