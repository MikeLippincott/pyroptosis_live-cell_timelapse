#!/bin/bash

# activate the conda environment
conda activate pyroptosis_timnelapse_env

# convert the notebooks to scripts
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
cd scripts || exit

# run the scripts
# python 0.preprocess_profiles.py
# python 1.eda_compute.py

conda deactivate
conda activate pyroptosis_timelapse_R

Rscript 2.eda_vizualize.r --dataset "first_time"
Rscript 2.eda_vizualize.r --dataset "pan_time"
Rscript 2.eda_vizualize.r --dataset "within_time"

cd .. || exit

echo "EDA completed successfully"
