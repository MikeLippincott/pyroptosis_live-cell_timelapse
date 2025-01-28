#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --qos=long
#SBATCH --account=amc-general
#SBATCH --time=60:00:00
#SBATCH --output=../pcp-%j.out

jid0=$(sbatch 0.merge_sc_parent.sh | awk '{print $4}')
jid1=$(sbatch --dependency=afterok:$jid0 1.annotate_sc_parent.sh | awk '{print $4}')
jid2=$(sbatch --dependency=afterok:$jid1 2.combine_sc.sh | awk '{print $4}')
jid3=$(sbatch --dependency=afterok:$jid2 3.normalize_sc.sh | awk '{print $4}')
jid4=$(sbatch --dependency=afterok:$jid3 4.feature_select_sc.sh | awk '{print $4}')
jid5=$(sbatch --dependency=afterok:$jid4 5.aggregate_sc.sh | awk '{print $4}')


echo "merge sc job id: $jid0"
echo "annotate sc job id: $jid1"
echo "combine sc job id: $jid2"
echo "normalize sc job id: $jid3"
echo "feature select sc job id: $jid4"
echo "aggregate sc job id: $jid5"

# get the efficiencies of the jobs
module load slurmtools
seff $jid0
seff $jid1
seff $jid2
seff $jid3
seff $jid4
seff $jid5

echo "Cellprofiling processing completed."
