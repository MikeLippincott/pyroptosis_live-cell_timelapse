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
# data_dir="../../../data/raw/"
data_dir="../../../data/test_dir"
mapfile -t FOV_dirs < <(ls -d $data_dir/*)
cd ../ || exit

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
    job_id=$(sbatch run_ic_child_HPC.sh "$FOV_dir")
	echo " '$job_id' '$FOV_dir' "
    echo " '$job_id' " >> job_ids.txt

    # append the job id to the file
    job_id=$(echo $job_id | awk '{print $4}')
    let jobs_submitted_counter++
done

# check that all jobs run successfully
while [ $(squeue -u $USER | wc -l) -gt 2 ]; do
    sleep 1s
done

conda deactivate

echo "All illumination correction jobs submitted!"
