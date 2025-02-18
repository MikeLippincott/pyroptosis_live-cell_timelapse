#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=0:30:00
#SBATCH --output=ic_child-%j.out

# This script runs Illumination Correction on the raw image data.
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

cd scripts/ || exit

python 0.perform_ic.py --input_dir "$1"

cd ../ || exit

conda deactivate

echo "Illumination Correction complete!"
