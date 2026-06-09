#!/bin/bash


source ~/.bashrc
conda activate timelapse_ibp_env

cd scripts || exit

well_fov=$1
python 0b.merge_sc_parallel.py --well_fov "$well_fov"

conda deactivate
cd ../  || exit
