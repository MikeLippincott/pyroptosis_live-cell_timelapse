#!/bin/bash

module load miniforge
conda init bash
conda activate cellprofiler_timelapse_env

cd scripts/ || exit

python 1.one_off_analysis_computational_requirments_for_fs.py --num_of_features $1 --num_of_cells_per_well $2 --num_of_wells $3

cd ../ || exit

conda deactivate

echo "Done"
