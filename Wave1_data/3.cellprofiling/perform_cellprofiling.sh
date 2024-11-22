#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=50
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=8:00:00
#SBATCH --output=../cp-%j.out

# 50 cores at 3.75 GB of ram per core puts us under the max ram for this node :D

# activate cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python run_cellprofiler_analysis.py

cd .. || exit

# deactivate cellprofiler environment
conda deactivate

echo "Cellprofiler analysis done"
