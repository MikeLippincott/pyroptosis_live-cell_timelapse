#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amem
#SBATCH --mem=950G
#SBATCH --qos=long
#SBATCH --account=amc-general
#SBATCH --time=7-00:00:00
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

cd scripts/ || exit

for feature_num in "${num_features[@]}"; do
    for num_cell in "${num_cells[@]}"; do
        for num_well in "${num_wells[@]}"; do
            echo "Running for feature_num: $feature_num, num_cells: $num_cell, num_well: $num_well"
            python 1.one_off_analysis_computational_requirments_for_fs.py --num_of_features "$feature_num" --num_of_cells_per_well "$num_cell" --num_of_wells "$num_well"
        done
    done
done


conda deactivate

echo "Done"
