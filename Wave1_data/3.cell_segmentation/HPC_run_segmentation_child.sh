#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=aa100
#SBATCH --gres=gpu:1
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=10:00
#SBATCH --output=segmentation-%j.out

module load anaconda

conda activate timelapse_segmentation_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts || exit

dir=$1

echo "$dir"
python 0.nuclei_segmentation.py --input_dir "$dir" --clip_limit 0.6 --optimize_segmentation False
python 1.cell_segmentation.py --input_dir "$dir" --clip_limit 0.6 --optimize_segmentation False

cd .. || exit

conda deactivate

echo "Segmentation done"
