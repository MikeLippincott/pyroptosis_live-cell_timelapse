#!/bin/bash

conda activate timelapse_segmentation_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

# param set if running the list top down and bottom up in parallel,
# to avoid overlap of the same well_fov
HALF_AND_HALF_OFF=1

cd scripts || exit

loadfile_path="../loadfiles/loadfile.txt"
mkdir -p "../logs"
progress_counter=0
total_lines=$(wc -l < "$loadfile_path")
while IFS= read -r well_fov; do
    echo "Processing $well_fov ($((++progress_counter)) of $total_lines)"
    # if the progress counter is halfway, divert and quit the script
    if [ "$progress_counter" -eq $((total_lines / 2)) ] && [ "$HALF_AND_HALF_OFF" -eq 1 ]; then
        echo "Halfway through the loadfile. Diverting to another script."
        echo "Exiting the bash script."
        exit 0
    fi

    log_file="../logs/$(basename "$well_fov" .txt).log"
    {
        python 1.nuclei_segmentation.py --well_fov "$well_fov" --clip_limit 0.6
        python 2.cell_segmentation.py --well_fov "$well_fov" --clip_limit 0.3
    } >> "$log_file"

# done < "$loadfile_path"
done < <(tac "$loadfile_path")

cd .. || exit

conda deactivate

echo "Segmentation done"
