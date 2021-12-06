#!/bin/bash -l
#SBATCH --account=rgutenk
#SBATCH --qos=user_qos_rgutenk
#SBATCH --partition=high_priority
#SBATCH --job-name="test_readme_full"
#SBATCH --output=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=94
###SBATCH --ntasks-per-node=50
#SBATCH --time=24:00:00

# rm -r ./examples/results/*
# mkdir ./examples/results/fs
# mkdir ./examples/results/fs/bootstrapping_syn
# mkdir ./examples/results/fs/bootstrapping_non
# mkdir ./examples/results/demo
# mkdir ./examples/results/caches
# mkdir ./examples/results/dfe
# mkdir ./examples/results/plots
# mkdir ./examples/results/stat

#
echo Generate synonymous SFS
#
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized \
--output ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs

#
echo Generate nonsynonymous SFS
#
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized \
--output ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs

#
echo Infer split migration demographic model
#
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid \
--p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 \
--output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 5 --threads 5 --maxeval 200 \
--force-convergence

#
echo Command to make .bestfits file
#
dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM \
--model split_mig --misid

#
echo Generate cache with shared population-scaled selection coefficients
#
dadi-cli GenerateCache --model split_mig --single-gamma \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--misid --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --mp

#
echo Generate cache with independent population-scaled selection coefficients
#
dadi-cli GenerateCache --model split_mig \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--misid --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --mp

#
echo Infer DFE that is a mixture of lognormal and bivariate lognormal
#
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 \
--lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params \
--optimizations 5 --threads 5 --maxeval 400 --force-convergence

#
echo Bootstrapping
#
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 100 \
--chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold

dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 100 \
--chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold

#
echo Godambe
#
dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--grids 60 80 100 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ \
--output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci

dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--model split_mig --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--pdf1d lognormal --pdf2d biv_lognormal --grids 60 80 100 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_non/ \
--output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.lognormal_mixture.params.godambe.ci

#
echo Plot synonymous SFS
#
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.unfold.fs.pdf \
--model split_mig

#
echo Plot nonsynonymous SFS
#
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs.pdf \
--model split_mig

#
echo Plot comparison between synonymous and nonsynonymous SFS
#
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--fs2 ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf \
--model None

#
echo Plot synonymous SFS vs infered split migration demographic model
#
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--misid --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.vs.split_mig.pdf \
--model split_mig --projections 30 30

#
echo Plot nonsynonymous SFS vs infered mixture model
#
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--misid --model split_mig \
--pdf1d lognormal --pdf2d biv_lognormal \
--dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.vs.lognormal_mixture.pdf



# work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -w 5 &
# dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid \
# --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 \
# --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 5 --threads 5 --maxeval 200 \
# --force-convergence \
# --work-queue test-dm-two-epoch ./tests/mypwfile


# work_queue_factory -T local -M test-dfe-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -W 30 &
# dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
# --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
# --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
# --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 \
# --lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 \
# --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
# --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params \
# --optimizations 5 --threads 5 --maxeval 400 \
# --force-convergence --delta-ll 0.1 \
# --work-queue test-dfe-two-epoch ./tests/mypwfile
























