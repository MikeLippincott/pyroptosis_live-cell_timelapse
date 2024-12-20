#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --partition=amem
#SBATCH --mem=300G
#SBATCH --qos=mem
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=normalize_sc-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit


python 3.normalize_sc_across_time.py
python 3.normalize_sc_within_time.py
python 3.normalize_sc_against_first_time.py


cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Normalizing sc processing completed."
