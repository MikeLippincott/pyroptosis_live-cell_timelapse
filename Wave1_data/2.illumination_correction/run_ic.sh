#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=60
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=10:00:00
#SBATCH --output=../ic-%j.out

# This script runs Illumination Correction on the raw image data.
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 0.perform_ic.py

cd ../ || exit

conda deactivate

echo "Illumination Correction complete!"
