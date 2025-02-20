#!/bin/bash

# activate the conda environment
conda activate pyroptosis_timnelapse_env

# convert the notebooks to scripts
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
cd scripts || exit

# run the scripts
# python 1.eda_compute.py # this gets run on the HPC due to memory requirements
python 3.timelapse_visualization.py

conda deactivate
conda activate pyroptosis_timelapse_R

Rscript 2.eda_vizualize.r --dataset "first_time"
Rscript 4.cell_count_analysis.r

cd .. || exit

conda deactivate

echo "EDA completed successfully"
