# Statistical testing

To perform uncertainty analysis, `dadi` offers [an approach](https://dadi.readthedocs.io/en/latest/user-guide/uncertainty-analysis/) using the Godambe Information Matrix (GIM). To utilize this method, users should begin by using the `GenerateFs` subcommand to generate bootstrapped data from VCF files.

In this example, we generate `20` bootstraps using the `--bootstrap` argument to save time, though we recommend users perform `100` bootstraps for more robust results. The `--chunk-size` argument specifies the maximum length of the chromosome chunks, which are then randomly drawn with replacement to create the bootstrapped chromosomes. The `--output` argument sets the prefix for the output files and the directory where the allele frequency spectra from the bootstrapped chromosomes will be stored.

```
dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.syn.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.syn

dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.non.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.non
```

The output files from the above commands can be found in the `bootstrapping_syn` directory for synonymous SNPs and the `bootstrapping_non` directory for non-synonymous SNPs [here](https://github.com/xin-huang/dadi-cli/tree/revision/examples/results/fs). 

To estimate the confidence intervals for the demographic parameters, users can use

```         
dadi-cli StatDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --grids 60 80 100 --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demog.params.godambe.ci
```

To estimate the confidence intervals for the joint DFE parameters, users can use

```         
dadi-cli StatDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --bootstrapping-nonsynonymous-dir ./examples/results/fs/bootstrapping_non/ --bootstrapping-synonymous-dir ./examples/results/fs/bootstrapping_non/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci
```

Three different step sizes are tested when using the GIM. Ideally 95% confidence intervals will be consistent between step sizes.
