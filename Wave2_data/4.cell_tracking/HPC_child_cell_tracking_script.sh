#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=30:00
#SBATCH --partition=aa100
#SBATCH --qos=gpu-normal
#SBATCH --gres=gpu:1
#SBATCH --output=cell_tracking-%j.out

module load miniforge
module load cuda/11.8
conda init bash
conda activate cell_tracking_env


jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

plate_name=$1
well_fov=$2
python 1c.nuclei_tracking_HOCT.py --well_fov "$well_fov" --plate_name "$plate_name"

cd ../ || exit

conda deactivate

echo "Cell tracking script completed"
