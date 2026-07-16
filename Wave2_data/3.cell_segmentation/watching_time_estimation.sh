#!/bin/bash

cd scripts || exit 1
conda activate pyroptosis_timelapse_env

iteration_count=0
# if 10 minute interval loop for 1000 iterations
# or 6.9 days
while [ "$iteration_count" -lt 1000 ]; do
    python watching_time_estimation.py
    sleep 600 # Wait for 10 minutes
    iteration_count=$((iteration_count + 1))
done

conda deactivate
cd ../ || exit 1
