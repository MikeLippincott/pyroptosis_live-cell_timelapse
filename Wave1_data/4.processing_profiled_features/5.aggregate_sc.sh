#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amem
#SBATCH --mem=300G
#SBATCH --qos=mem
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=agg-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 5.aggregate_profiles.py

cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Aggregation completed."
