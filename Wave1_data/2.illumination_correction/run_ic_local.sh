#!/bin/bash


# This script runs Illumination Correction on the raw image data.
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to python --output-dir=scripts/ notebooks/*.ipynb

cd scripts/ || exit

# testing dir
input_dir="../../../data/test_dir/W0052_F0001"

python 0.perform_ic.py --input_dir "$input_dir"

cd ../ || exit

conda deactivate

echo "Illumination Correction complete!"
