#!/bin/bash

#SBATCH --account=rgutenk
#SBATCH --partition=high_priority
#SBATCH --qos=user_qos_rgutenk
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=01:00:00
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5  --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 10 --maxeval 20 --seed 12345 --cpus 4