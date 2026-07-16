#!/bin/bash

plate=$1
if [ -z "$plate" ]; then
    echo "Error: No plate name provided. Please provide a plate name as an argument."
    exit 1
fi

# activate the preprocessing environment
conda activate pyroptosis_timelapse_env

jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb


# run feature extraction
cd scripts || exit 0
conda activate pyroptosis_timelapse_env
python check_for_file_completion.py --plate_name "$plate"
python generate_load_data.py --plate_name "$plate"
python run_cellprofiler_analysis.py --plate_name "$plate" --max_workers 48
conda deactivate
cd ../ || exit 0
