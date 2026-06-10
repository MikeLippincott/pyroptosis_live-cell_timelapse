#!/bin/bash
#SBATCH --job-name=merge_sc_parallel
#SBATCH --output=merge_sc_parallel_%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --time=1-00:00:00
#SBATCH --account=math-alderaan

# establish the git root and load the list of well_fov_times to process
git_root=$(git rev-parse --show-toplevel)
# establish the load data and load it into an array
load_data_well_fov_file_path="${git_root}/Wave2_data/6.image_based_profiling/load_data/load_file_well_fov.txt"

readarray -t well_fovs < "$load_data_well_fov_file_path"

source ~/.bashrc
conda activate timelapse_ibp_env

# Optional: regenerate scripts from notebooks
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb


python 00.generate_load_list.py
cd ../ || exit

counter=0
total=${#well_fovs[@]}
for well_fov in "${well_fovs[@]}"; do
    echo "Processing $well_fov ($((counter+1))/$total)..."
    ((counter++))
    python 0b.merge_sc_parallel.py --well_fov "$well_fov" --max_workers 64
done

conda deactivate
cd ../ || exit
