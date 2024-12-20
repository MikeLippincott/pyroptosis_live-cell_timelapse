#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --partition=amilan
#SBATCH --mem=100G
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=merge_sc-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 0.merge_sc.py

cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Merge sc processing completed."
