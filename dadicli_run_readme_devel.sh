#!/bin/bash -l
#SBATCH --account=rgutenk
#SBATCH --qos=user_qos_rgutenk
#SBATCH --partition=high_priority
#SBATCH --job-name="test_readme_full"
#SBATCH --output=%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=90
###SBATCH --ntasks-per-node=90
#SBATCH --time=24:00:00

# rm -r ./examples/results/*
mkdir ./examples/results/fs
mkdir ./examples/results/fs/bootstrapping_syn
mkdir ./examples/results/fs/bootstrapping_non
mkdir ./examples/results/demo
mkdir ./examples/results/caches
mkdir ./examples/results/dfe
mkdir ./examples/results/plots
mkdir ./examples/results/stat

#
echo Generate synonymous SFS
#
time dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized \
--output ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs

#
echo Generate nonsynonymous SFS
#
time dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized \
--output ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs


echo Infer split migration demographic model
#
time dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--model split_mig --p0 2 0.5 .25 1.2 .02 --ubounds 3 1 0.3 2 0.03 --lbounds 1 1e-1 1e-1 1 1e-3 \
--grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 50 --maxeval 100 \
--force-convergence
#--global-optimization

#
echo Import model and Infer split migration demographic model
#
time dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--model split_mig_fix_T --model-file examples/data/split_mig_fix_T_models \
--p0 2 0.5 1.2 .02 --ubounds 3 1 2 0.03 --lbounds 1 1e-1 1e-1 1e-3 \
--grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params --optimizations 50 --maxeval 300 \
--force-convergence 
#--global-optimization

#
echo GIM for DM
#
time dadi-cli StatDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--model split_mig_fix_T --model-file examples/data/split_mig_fix_T_models --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_psudo_new_model.demo.params.InferDM.bestfits \
--grids 60 80 100 --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ \
--output ./examples/results/stat/1KG.YRI.CEU.20.split_mig_psudo_new_model.bestfit.demo.params.godambe.ci

# work_queue_factory -T local -M test-demo-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -E '--connection-mode by_apparent_ip' --cores=1 -t 10 -w 10 -W 10 &
# time dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
# --model split_mig --p0 2 0.5 .25 1.2 .02 --ubounds 3 1 0.3 2 0.03 --lbounds 1 1e-1 1e-1 1 1e-3 \
# --grids 60 80 100 --output 1KG.YRI.CEU.20.wq.split_mig.demo.params --optimizations 10 --maxeval 5 \
# --check-convergence --work-queue test-demo-two-epoch ./tests/mypwfile --global-optimization &

# work_queue_factory -T amazon --amazon-config my.config -M test-demo-two-epoch -P dadicli/tests/mypwfile --workers-per-cycle=0 -d all -E '--connection-mode by_apparent_ip' & --cores=1-t 10 -w 1 -W 1 &
# time dadi-cli InferDM --fs dadicli/examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
# --model split_mig --p0 2 0.5 .25 1.2 .02 --ubounds 3 1 0.3 2 0.03 --lbounds 1 1e-1 1e-1 1 1e-3 \
# --grids 60 80 100 --output 1KG.YRI.CEU.20.wq.split_mig.demo.params --optimizations 20 --maxeval 100 \
# --check-convergence --work-queue test-demo-two-epoch dadicli/tests/mypwfile &

#
echo Command to make .bestfits file
#
time dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM \
--ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5

#
echo Generate cache with shared population-scaled selection coefficients
#
time dadi-cli GenerateCache --model split_mig_sel_single_gamma \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--sample-size 20 20 --grids 160 180 200 --gamma-pts 20 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --mp

#
echo Generate cache with independent population-scaled selection coefficients
#
time dadi-cli GenerateCache --model split_mig_sel --dimensionality 2 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--sample-size 20 20 --grids 160 180 200 --gamma-pts 20 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --mp

#
echo Import model and Generate cache with shared population-scaled selection coefficients
#
time dadi-cli GenerateCache --model split_mig_fix_T_one_s --model-file examples/data/split_mig_fix_T_models \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits \
--sample-size 20 20 --grids 160 180 200 --gamma-pts 20 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_one_s_psudo_new_model.spectra.bpkl --mp

#
echo Import model and generate cache with independent population-scaled selection coefficients
#
time dadi-cli GenerateCache --model split_mig_fix_T_sel --model-file examples/data/split_mig_fix_T_models --dimensionality 2 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits \
--sample-size 20 20 --grids 160 180 200 --gamma-pts 20 --gamma-bounds 1e-4 200 \
--output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_psudo_new_model.spectra.bpkl --mp

#
echo Infer 1D lognormal DFE
#
time dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--pdf1d lognormal --lbounds 0 0.01 0 --ubounds 10 10 1 --p0 1 1 .5 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params \
--optimizations 50 --maxeval 400 --check-convergence &

#
echo Infer bivariate symetric lognormal DFE
#
time dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--pdf2d biv_lognormal --p0 1 1 .8 .5 --lbounds 0 0.01 0.001 0 --ubounds 10 10 0.999 1 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 \
--output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_sym_lognormal.params \
--optimizations 50 --maxeval 400 --check-convergence &

#
echo Infer bivariate asymetric lognormal DFE 
#
time dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds 0 0 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 1 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 \
--output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_asym_lognormal.params \
--optimizations 50 --maxeval 400 --check-convergence &

#
echo Infer DFE that is a mixture of lognormal and bivariate lognormal
#
time dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--pdf1d lognormal --pdf2d biv_lognormal --mix-pdf mixture_lognormal \
--p0 1 1 0 .5 .5 --lbounds 0 0.01 -1 0.001 0 --ubounds 10 10 -1 0.999 1 --constants -1 -1 0 -1 -1 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params \
--optimizations 50 --maxeval 400 --check-convergence

#
echo Bootstrapping
#
time dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 \
--chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold &

time dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz \
--pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 \
--chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold

#
echo Godambe
#
time dadi-cli StatDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--grids 60 80 100 --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ \
--output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci &

time dadi-cli StatDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--pdf1d lognormal \
--bootstrapping-synonymous-dir ./examples/results/fs/bootstrapping_syn/ \
--bootstrapping-nonsynonymous-dir ./examples/results/fs/bootstrapping_non/ \
--output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci

#
echo Plot synonymous SFS
#
time dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.unfold.fs.pdf \
--model split_mig

#
echo Plot nonsynonymous SFS
#
time dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs.pdf \
--model split_mig

#
echo Plot comparison between synonymous and nonsynonymous SFS
#
time dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--fs2 ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf \
--model None

#
echo Plot synonymous SFS vs infered split migration demographic model
#
time dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.vs.split_mig.pdf \
--model split_mig

#
echo Plot nonsynonymous SFS vs infered mixture model
#
time dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--model split_mig \
--pdf1d lognormal --pdf2d biv_lognormal \
--dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.vs.lognormal_mixture.pdf



work_queue_factory -T local -M test-dm-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -W 5 &
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid \
--p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 \
--output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 5 --maxeval 100 \
--work-queue test-dm-two-epoch ./tests/mypwfile --check-convergence

work_queue_factory -T local -M test-dfe-two-epoch -P ./tests/mypwfile --workers-per-cycle=0 -t 10 --cores=1  -W 5 &
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs \
--cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl \
--cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl \
--misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 \
--lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 \
--demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits \
--ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params \
--optimizations 5 --maxeval 400 \
--force-convergence --delta-ll 0.1 \
--work-queue test-dfe-two-epoch ./tests/mypwfile
























