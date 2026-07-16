#!/bin/bash


conda activate pyroptosis_timelapse_env
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb


plate=$1
if [ -z "$plate" ]; then
    echo "Error: No plate name provided. Please provide a plate name as an argument."
    exit 1
fi

# param set if running the list top down and bottom up in parallel,
# to avoid overlap of the same well_fov
HALF_AND_HALF=0

cd scripts || exit
python 0.generate_load_file.py --plate_name "$plate"
loadfile_path="../loadfiles/loadfile.txt"
mkdir -p "../logs"
progress_counter=0
total_lines=$(wc -l < "$loadfile_path")
conda deactivate ; conda activate timelapse_segmentation_env
while IFS= read -r well_fov; do
    echo "Processing $well_fov ($((++progress_counter)) of $total_lines)"
    # if the progress counter is halfway, divert and quit the script
    if [ "$progress_counter" -eq $((total_lines / 2)) ] && [ "$HALF_AND_HALF" -eq 1 ]; then
        echo "Halfway through the loadfile. Diverting to another script."
        echo "Exiting the bash script."
        exit 0
    fi

    log_file="../logs/$(basename "$well_fov" .txt).log"
    {
        python 1.nuclei_segmentation.py --well_fov "$well_fov" --clip_limit 0.6 --plate_name "$plate"
        python 2.cell_segmentation.py --well_fov "$well_fov" --clip_limit 0.3 --plate_name "$plate"
    } >> "$log_file"

done < "$loadfile_path"
# done < <(tac "$loadfile_path")

cd .. || exit

conda deactivate

echo "Segmentation done"
