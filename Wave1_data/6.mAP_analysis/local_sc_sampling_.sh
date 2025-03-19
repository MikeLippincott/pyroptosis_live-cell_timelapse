#!/bin/bash

conda activate timelapse_map_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

# read percentage of parent cells from file
mapfile -t percentage < ./combinations/percentage.txt
mapfile -t seeds < ./combinations/seeds.txt

cd scripts/ || exit

for percent in "${percentage[@]}"; do
    for seed in "${seeds[@]}"; do

        python 2.run_map_on_percentages_of_cells.py --percentage "$percent" --seed "$seed"
        python 2.run_map_on_percentages_of_cells.py --percentage "$percent" --seed "$seed" --shuffle

    done
done

cd .. || exit

conda deactivate

echo "Parent cell sampling jobs submitted"
