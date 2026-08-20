#!/bin/bash
# establish the git root and load the list of well_fov_times to process
git_root=$(git rev-parse --show-toplevel)
# establish the load data and load it into an array
load_data_file_path="${git_root}/Wave2_data/6.image_based_profiling/load_data/load_file_well_fov.txt"

MAX_JOBS=8

readarray -t well_fovs < "$load_data_file_path"

conda activate timelapse_ibp_env

# Optional: regenerate scripts from notebooks
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts || exit

python 00.generate_load_list.py --plate_name "plate_2"
# python 0.merge_sc.py
# python 1.combine_sc.py
# python 2.qc.py
# python 3.annotate_sc.py
# python 5.single_cell_track_merging_placeholder.py
# python 6.normalize_sc.py
# python 7.feature_select_sc.py
# python 8.aggregate_profiles.py

conda deactivate ; conda activate timelapse_deeplearning_env

for well_fov in "${well_fovs[@]}"; do
    echo "Featurizing for well_fov: $well_fov"
    python 4a.chammi75_featurization.py -plate_name "plate_2" --well_fov "$well_fov" &

    # If we've hit the limit, wait for any one job to finish before continuing
    if (( $(jobs -r -p | wc -l) >= MAX_JOBS )); then
        wait -n
    fi
done

# Wait for any remaining background jobs to finish
wait

conda deactivate ; conda activate timelapse_ibp_env

# python 9.harmonize_profiles.py

# conda deactivate
# cd ../  || exit
