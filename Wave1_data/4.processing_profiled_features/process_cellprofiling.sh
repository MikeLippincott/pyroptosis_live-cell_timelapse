#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=long
#SBATCH --account=amc-general
#SBATCH --time=60:00:00
#SBATCH --output=main_parent-%j.out

jid1=$(sbatch 2.combine_sc.sh | awk '{print $4}')
jid2=$(sbatch --dependency=afterok:$jid1 3.normalize_sc.sh | awk '{print $4}')
jid3=$(sbatch --dependency=afterok:$jid2 4.feature_select_sc.sh | awk '{print $4}')
jid4=$(sbatch --dependency=afterok:$jid3 5.aggregate_sc.sh | awk '{print $4}')



seff $jid1
seff $jid2
seff $jid3
seff $jid4

echo "Cellprofiling processing completed."
