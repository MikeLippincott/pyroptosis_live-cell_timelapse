#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=600G
#SBATCH --partition=amem
#SBATCH --qos=mem
#SBATCH --account=amc-general
#SBATCH --time=24:00:00
#SBATCH --output=sample-%j.out

module load anaconda
conda init bash

# activate the conda environment
conda activate pyroptosis_timelapse_env

# convert the notebooks to scripts
jupyter nbconvert --to=script --FilesWriter.build_directory=scripts/ notebooks/*.ipynb
cd scripts || exit

# run the scripts
python 1.eda_compute.py
python 3.timelapse_visualization.py

conda deactivate
conda activate pyroptosis_timelapse_R

Rscript 2.eda_vizualize.r
Rscript 4.cell_count_analsis.r
Rscript 5.plot_platemap.r
Rscript 6.bulk_analysis.r
Rscript 7.umap_videos.r

conda deactivate

echo "EDA completed successfully"
