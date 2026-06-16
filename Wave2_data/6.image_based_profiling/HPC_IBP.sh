#!/bin/bash
#SBATCH --job-name=ibp_pipe
#SBATCH --output=ibp_pipe%A_%a.out
#SBATCH --nodes=1
#SBATCH --mem=600G
#SBATCH --time=2:00:00 # D-HH:MM:SS
#SBATCH --partition=highmem
#SBATCH --account=bio260064

# establish the git root and load the list of well_fov_times to process
git_root=$(git rev-parse --show-toplevel)
# establish the load data and load it into an array
load_data_well_fov_file_path="${git_root}/Wave2_data/6.image_based_profiling/load_data/load_file_well_fov.txt"

readarray -t well_fovs < "$load_data_well_fov_file_path"

module load anaconda
conda activate timelapse_ibp_env

# Optional: regenerate scripts from notebooks
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit
python 00.generate_load_list.py

echo "Combining sc"
python 1.combine_sc.py
echo "Single cells combined. Starting QC."
python 2.qc.py
echo "QC done. Starting annotation."
python 3.annotate_sc.py
echo "Annotation done. Starting single cell track merging placeholder."
# python 5.single_cell_track_merging_placeholder.py
# echo "Single cell track merging placeholder done. Starting normalization."
# python 6.normalize_sc.py
# echo "Normalization done. Starting feature selection."
# python 7.feature_select_sc.py
# echo "Feature selection done. Starting profile aggregation."
# python 8.aggregate_profiles.py
# echo "Profile aggregation done. Starting featurization."

# conda deactivate ; conda activate timelapse_deeplearning_env
# for well_fov_time in "${well_fov_times[@]}"; do
#     echo "Featurizing for well_fov_time: $well_fov_time"
#     python 4a.chammi75_featurization.py --well_fov_time "$well_fov_time"
# done
# python 4b.chammi75_combine_sc.py

# conda deactivate ; conda activate timelapse_ibp_env

# python 9.harmonize_profiles.py

conda deactivate
cd ../  || exit
