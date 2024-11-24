#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=200G
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=sample-%j.out

module load anaconda
conda init bash

# activate the conda environment
conda activate pyroptosis_timelapse_env

# convert the notebooks to scripts
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
cd scripts || exit

# run the scripts
python 0.preprocess_profiles.py
python 1.eda_compute.py

conda deactivate
conda activate pyroptosis_timelapse_R

Rscript 2.eda_vizualize.r --dataset "first_time"
Rscript 2.eda_vizualize.r --dataset "pan_time"
Rscript 2.eda_vizualize.r --dataset "within_time"

echo "EDA completed successfully"
