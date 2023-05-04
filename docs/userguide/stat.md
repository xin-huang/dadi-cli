# Statistical testing

To performing statistical testing with the Godambe Information Matrix (GIM), users should first use `GenerateFs` to generate bootstrapping data from VCF files. In this example we generate 20 bootstraps to save on time, but we recommend users do 100. `--chunk-size` is the max length of chunks the chromosomes will be broken up into and used to randomly draw from with replacement to make our bootstrapped chromosomes.

```         
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold

dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold
```

To estimate the confidence intervals for the demographic parameters, users can use

```         
dadi-cli StatDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --grids 60 80 100 --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demog.params.godambe.ci
```

To estimate the confidence intervals for the joint DFE parameters, users can use

```         
dadi-cli StatDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --bootstrapping-nonsynonymous-dir ./examples/results/fs/bootstrapping_non/ --bootstrapping-synonymous-dir ./examples/results/fs/bootstrapping_non/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci
```

Three different step sizes are tested when using the GIM. Ideally 95% confidence intervals will be consistent between step sizes.
