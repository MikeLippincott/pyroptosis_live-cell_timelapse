#!/bin/bash

conda activate timelapse_segmentation_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts || exit

illumination_correction_dir="../../2.illumination_correction/illum_directory/"

mapfile -t dirs < <(ls -d "$illumination_correction_dir"/*)

for dir in "${dirs[@]}"; do
    python 0.nuclei_segmentation.py --input_dir "$dir"
    python 1.cell_segmentation.py --input_dir "$dir"
done

cd .. || exit

conda deactivate

echo "Segmentation done"
