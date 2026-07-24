#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --time=2:00:00
#SBATCH --partition=aa100
#SBATCH --qos=gpu-normal
#SBATCH --gres=gpu:a100-40gb:1
#SBATCH --output=cell_tracking-%j.out

module load miniforge
module load cuda/13.0
conda init bash
conda activate cell_tracking_env


cd scripts/ || exit

plate_name=$1
well_fov=$2
python 1c.nuclei_tracking_HOCT.py --well_fov "$well_fov" --plate_name "$plate_name"

cd ../ || exit

conda deactivate

echo "Cell tracking script completed"
