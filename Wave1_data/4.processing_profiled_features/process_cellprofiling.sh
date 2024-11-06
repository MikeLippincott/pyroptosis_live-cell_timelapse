#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --account=amc-general
#SBATCH --time=06:00:00
#SBATCH --output=../pcp-%j.out

# activate  cellprofiler environment
module load anaconda
conda init bash
conda activate cellprofiler_timelapse_env

jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb

cd scripts/ || exit

python 0.merge_sc.py
python 1.annotate_sc.py
python 2.combine_sc.py
# python 3.normalize_sc_across_time.py
# python 3.normalize_sc_within_time.py
# python 4.feature_select_sc.py

cd ../ || exit

# deactivate cellprofiler environment
conda deactivate

echo "Cellprofiling processing completed."
