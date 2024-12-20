#!/bin/bash

# This script is used to preprocess the raw data

conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 0.preprocess_raw_data.py
python 1.define_platemap.py

cd .. || exit

conda deactivate

echo "Preprocessing done!"
