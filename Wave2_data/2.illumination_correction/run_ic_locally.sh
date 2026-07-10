#!/bin/bash

conda activate cellprofiler_timelapse_env
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

plate=$1
if [ -z "$plate" ]; then
    echo "Error: No plate name provided. Please provide a plate name as an argument."
    exit 1
fi

cd scripts || exit
python 0.generate_run_list.py --plate_name "$plate"
loadfile_path="../loadfiles/well_fovs_to_run.tsv"
counter=0
total_lines=$(wc -l < "${loadfile_path}")
echo "Total images to process: ${total_lines}"
while IFS=$'\t' read -r well_fov; do
    if [ "${well_fov}" == "well_fov" ]; then
        # Skip the header line
        continue
    fi
    # run the Python script with the current well_fov as an argument
    # takes about 15 min per 102 timepoints for 5 channels
    # which this script runs
    python 1.perform_ic_cp.py --well_fov "${well_fov}" --plate_name "$plate"
    # update the counter and print progress
    counter=$((counter + 1))
    echo "Processed ${counter} of ${total_lines} images"

done < "${loadfile_path}"

cd ../ || exit
echo "Finished running IC for all images."
