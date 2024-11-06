#!/bin/bash

# This script runs Illumination Correction on the raw image data.
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 0.perform_ic.py

cd ../ || exit

conda deactivate

echo "Illumination Correction complete!"
