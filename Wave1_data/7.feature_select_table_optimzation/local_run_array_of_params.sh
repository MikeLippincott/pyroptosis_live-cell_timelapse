#!/bin/bash

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
    for num_cells in "${num_cells[@]}"; do
        for num_well in "${num_wells[@]}"; do
            echo "Running for feature_num: $feature_num, num_cells: $num_cells, num_groups: $num_well"
            python 1.one_off_analysis_computational_requirments_for_fs.py --num_of_features $feature_num --num_of_cells_per_well $num_cells --num_of_wells $num_well
        done
    done
done

python 2.concat_profiling_results.py

cd ../ || exit


conda deactivate

echo "Done"
