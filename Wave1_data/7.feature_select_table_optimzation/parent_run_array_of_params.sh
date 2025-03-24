#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=10:00:00
#SBATCH --output=ic_parent-%j.out

module load miniforge
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to python --output-dir=scripts/ notebooks/*.ipynb

# define array of parameters
num_features_path="./arrays/num_of_features.txt"
num_cells_path="./arrays/num_of_cells_per_well.txt"
num_wells_path="./arrays/num_of_wells.txt"

mapfile -t num_features < "$num_features_path"
mapfile -t num_cells < "$num_cells_path"
mapfile -t num_wells < "$num_wells_path"

for feature_num in "${num_features[@]}"; do
    for num_cell in "${num_cells[@]}"; do
        for num_well in "${num_wells[@]}"; do
            echo "Running for feature_num: $feature_num, num_cells: $num_cell, num_well: $num_well"
            number_of_jobs=$(squeue -u $USER | wc -l)
            while [ $number_of_jobs -gt 990 ]; do
                sleep 1s
                number_of_jobs=$(squeue -u $USER | wc -l)
            done
            sbatch --nodes=1 --partition=amilan --qos=normal --account=amc-general --time=1:00:00 --output=ic_child-%j.out child_process_run_memory_profiling.sh "$feature_num" "$num_cell" "$num_well"
        done
    done
done


conda deactivate

echo "Done"
