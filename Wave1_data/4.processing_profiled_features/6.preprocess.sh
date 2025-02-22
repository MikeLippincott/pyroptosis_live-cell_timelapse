#!/bin/bash
#SBATCH --nodes=1
#SBATCH --partition=amem
#SBATCH --mem=900G
#SBATCH --qos=mem
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=preprocessing-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 6.preprocess_profiles.py --samples_per_group 25 --data_subset
python 6.preprocess_profiles.py --samples_per_group 25

cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Preprocessing completed."
