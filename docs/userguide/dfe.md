# DFE inference

## Generating caches for DFE inference

After inferring a best fit demographic model, users may also infer distributions of fitness effects (DFEs) from data. To perform DFE inference, users need to first generate of cache of frequency spectra. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel` model or the `split_mig_sel_single_gamma` model. The `split_mig_sel` model is used for inferring the DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are the same in the two populations. If users want to to make the cache for the situation where the selection coefficients are independent from one another, they should use the `--dimensionality 2` option. Users can use the `--gamma-bounds` option to choose the range of the gamma distribution and the `--gamma-pts` option can be used to specify the number of selection coefficients that will be selected in that range to generate the cache. Note that the higher (more negative) you make the `--gamma-bounds`, the bigger the grid points, altered via the `--grids` option, users will want to use.

Here is an example command to generate a cache with shared selection coefficients:
```         
dadi-cli GenerateCache --model split_mig_sel_single_gamma --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cpus 4
```
Here is an example command to generate a cache with independent selection coefficients:
```
dadi-cli GenerateCache --model split_mig_sel --dimensionality 2 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --cpus 4
```
Users will likely want to use larger `--gamma-bounds` and `--gamma-pts` than the example.

## Inferring DFE

For inferring the DFE, we fit the spectrum from nonsynonymous SNPs. Although our data come from two populations, we will first infer a one-dimensional DFE, which assumes that selection coefficients are equal in the two populations. We define the marginal DFE as a lognormal distribution with `--pdf1d`. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. Our parameters are `log_mu` the mean of the lognormal distribution, `log_sigma` the standard deviation of the lognormal distribution, and `misid`.

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence 5
```

The result is

```         
# /Users/user/anaconda3/envs/dadicli/bin/dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence 5
#
# Converged results
# Log(likelihood)   log_mu  log_sigma   misid   theta
-1388.7168092990519 5.490553018509483   7.617358688984522   0.016580353311106688    15644.214296668904
-1388.7182268917072 5.48833179537645    7.612505954083041   0.016574649919878663    15644.214296668904
-1388.7511876804606 5.465373979901826   7.565453530395414   0.01664401774234844 15644.214296668904
#
# Top 100 results
# Log(likelihood)   log_mu  log_sigma   misid   theta
-1388.7168092990519 5.490553018509483   7.617358688984522   0.016580353311106688    15644.214296668904
-1388.7182268917072 5.48833179537645    7.612505954083041   0.016574649919878663    15644.214296668904
-1388.7511876804606 5.465373979901826   7.565453530395414   0.01664401774234844 15644.214296668904
```

Similar to the best fit parameters in `./examples/results/demog/1KG.YRI.CEU.split_mig.bestfit.demog.params`, the first column is the log-likelihood followed by the parameters.

| likelihood | mu  | sigma | misidentification |
|------------|-----|-------|-------------------|
| -1389      | 5.5 | 7.6   | 0.017             |
