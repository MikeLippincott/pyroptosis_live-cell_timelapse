#!/bin/bash

# activate the preprocessing environment
conda activate pyroptosis_timelapse_env

jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb


cd scripts/ || exit

python generate_load_data.py --plate_name "plate_1"

python run_cellprofiler_analysis.py --max_workers 48 --plate_name "plate_1"

conda deactivate

echo "Cell segmentation preprocessing completed successfully."
