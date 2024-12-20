#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amem
#SBATCH --mem=750G
#SBATCH --qos=mem
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=fs_sc-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 4.feature_select_sc.py

cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Feature_selection processing completed."
