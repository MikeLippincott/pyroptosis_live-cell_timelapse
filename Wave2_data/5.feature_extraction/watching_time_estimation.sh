#!/bin/bash
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts || exit 1
conda activate pyroptosis_timelapse_env

iteration_count=0
# if 60 minute interval loop for 1000 iterations
# or 60,000 minutes, or 1,000 hours, or 41.6 days
while [ "$iteration_count" -lt 1000 ]; do
    python watching_time_estimation.py
    sleep 3600 # Wait for 60 minutes
    iteration_count=$((iteration_count + 1))
done

conda deactivate
cd ../ || exit 1
