# Plotting

`dadi-cli` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.unfold.fs.pdf

dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs.pdf
```

To compare two frequency spectra from data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --fs2 ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf --model None
```

To compare frequency spectra between a demographic model without selection and data, users will need a file from inferring the demography, `--demo-popt`, and the `--model` inferred:

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.vs.split_mig.pdf --model split_mig
```

To compare frequency spectra between a demographic model with selection and data, users will need the `--dfe-popt` file from inferring the DFE, the cache(s), `--cache1d` and/or `--cache2d`, and the PDF(s), `--pdf1d` and/or `--pdf2d`.

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --pdf1d lognormal --pdf2d biv_lognormal --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.vs.lognormal_mixture.pdf
```

By default, `dadi-cli` will use the sample size of the provided frequency spectrum, or smallest sample size(s) for each population if multiple frequency spectra are used. Users can use `--projections` to lower the sample size for visualization purposes.
