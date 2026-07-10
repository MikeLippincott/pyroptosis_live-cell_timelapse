#!/bin/bash

# run the gold standard pipeline for Wave2 data
# define plates to run on
plates=("plate_2")

# for plate in "${plates[@]}"; do
plate="plate_2"
echo "Running gold standard pipeline for $plate"

# preprocess the data
cd 1.preprocess_data/|| exit 0
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
cd scripts || exit 0
conda activate pyroptosis_timelapse_env
python 0.preprocess_raw_data.py --plate_name "$plate"
conda deactivate
cd ./../ || exit 0

# run illumination correction
cd 2.illumination_correction || exit 0
source run_ic_locally.sh "$plate"
cd ../ || exit 0

# run cell segmentation
cd 3.cell_segmentation/ || exit 0
source local_run_segmentation.sh "$plate"
cd ../ || exit 0

echo "Gold standard pipeline for $plate completed through segmentation step."

# run feature extraction
cd 5.feature_extraction/|| exit 0
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/generate_load_data.ipynb
cd scripts || exit 0
conda activate pyroptosis_timelapse_env
python check_for_file_completion.py --plate_name "$plate"
python generate_load_data.py --plate_name "$plate"
python run_cellprofiler_analysis.py --plate_name "$plate" --max_workers 48
conda deactivate
cd ./../ || exit 0
