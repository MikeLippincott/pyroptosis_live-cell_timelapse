#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --partition=amilan
#SBATCH --output=cell_tracking-%j.out

module load miniforge
conda init bash
conda activate cell_tracking_env


jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
plate_name=$1
cd scripts/ || exit

python 0.generate_load_file.py --plate_name "$plate_name"
load_file_path="../loadfiles/loadfile.txt"

while IFS= read -r well_fov; do
    dirname=$(basename "$dir")
    well_fov="${dirname#*MaxIP_}"
    echo "Well FOV: $well_fov"
    sbatch HPC_child_cell_tracking_script.sh "$well_fov" "$plate_name"
done

cd ../ || exit

conda deactivate

echo "Cell tracking script completed"
