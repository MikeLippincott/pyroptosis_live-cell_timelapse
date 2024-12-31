#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=10:00:00
#SBATCH --output=ic_parent-%j.out

# This script runs Illumination Correction on the raw image data.
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

# get a list of all dirs in the raw data folder
data_dir="../../../data/raw/"
mapfile -t plate_dirs < <(ls -d $data_dir*/)
mapfile -t FOV_dirs < <(ls -d $data_dir*/*/)

cd ../ || exit

echo length of plate_dirs: ${#plate_dirs[@]}
echo length of plate_dirs: ${#FOV_dirs[@]}

touch job_ids.txt
jobs_submitted_counter=0
for FOV_dir in "${FOV_dirs[@]}"; do
	# get the number of jobs for the user
    number_of_jobs=$(squeue -u $USER | wc -l)
    while [ $number_of_jobs -gt 990 ]; do
        sleep 1s
        number_of_jobs=$(squeue -u $USER | wc -l)
    done
	echo " '$job_id' '$FOV_dir' "
        echo " '$job_id' " >> job_ids.txt
        job_id=$(sbatch run_ic_child_HPC.sh "$dir")
        # append the job id to the file
        job_id=$(echo $job_id | awk '{print $4}')
        let jobs_submitted_counter++
done

# check that all jobs run successfully
while [ $(squeue -u $USER | wc -l) -gt 1 ]; do
    sleep 1s
done

for job_id in $(cat job_ids.txt); do
    job_id=$(echo $job_id | awk '{print $1}')
    job_status=$(sacct -j $job_id -o state | tail -n 1)
    if [ $job_status != "COMPLETED" ]; then
        echo "Job $job_id did not complete successfully"
        exit 1
    fi
done

conda deactivate

echo "All illumination correction jobs submitted!"
