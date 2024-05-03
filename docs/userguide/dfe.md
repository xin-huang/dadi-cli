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

# Joint DFE inference

## Inferring a bivariate lognormal joint DFE

Here we will infer a joint DFE with selection potentially being different in the two populations. We define the DFE as a bivariate lognormal distribution with `--pdf2d` and pass in a cache that assumes the population-scaled selection coefficients are different in the two populations through `--cache2d`. The bivariate lognormal has an extra parameter `rho`, the correlation of the DFE between the populations. We can allow `mu_log` and `sigma_log` be different or the same in our populations. `dadi-cli` will run either the symmetric (shared `mu_log` and `sigma_log`) or asymmetric (independent `mu_log` and `sigma_log`) bivariate lognormal based on the number of parameters. For the symmetric bivariate lognormal the parameters are `log_mu`, `log_sigma`, and `rho`, the asymmetric bivariate lognormal the parameters are `log_mu1`, `log_mu2`, `log_sigma1`, `log_sigma2`, and `rho`, where 1 denotes the first population and 2 denotes the second population.

An example of running a symmetrical bivariate lognormal is:

```
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 .5 .5 --lbounds -10 0.01 0.001 0 --ubounds 10 10 0.999 0.5 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_sym_lognormal.params --optimizations 15 --maxeval 400 --check-convergence 10
```

An example of running an asymmetrical bivariate lognormal is:

```
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_asym_lognormal.params --optimizations 15 --maxeval 400 --check-convergence 10
```

## Inferring mixture model joint DFE

Here, we will use a mixture of a univariate lognormal and a bivariate lognormal distribution. To make the mixture we pass in options for both 1D and 2D: `--pdf1d`, `--pdf2d`, `--cache1d`, and `--cache2d`. Because the mixture model is assuming some proportion of the DFE is lognormal and the other is bivariate, the bivariate is symmeteric. The parameters for the mixture lognormal DFE are `log_mu`, `log_sigma`, `rho`,and `w`, the proportional weight of the bivariate lognormal DFE (1-`w` would be the weight of the univariate lognormal distribution). In this example we fix `rho` of the bivariate component to 0 with the `--constants` option.

```
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --mix-pdf mixture_lognormal --p0 1 1 0 .5 .5 --lbounds -10 0.01 -1 0.001 0 --ubounds 10 10 -1 0.999 0.5 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 15 --maxeval 400 --check-convergence 10
```

Similar to the best fit parameters in `./examples/results/demog/1KG.YRI.CEU.split_mig.bestfit.demog.params`, the first column is the log-likelihood.

| likelihood | mu   | sigma | rho | w   | misidentification |
|------------|------|-------|-----|-----|-------------------|
| -1389      | 5.51 | 7.65  | 0   | 0   | 0.017             |

## Settings

| Argument | Description |
| - | - |
| `--fs`                  | Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link. |
| `--demo-popt`           | File contains the bestfit parameters for the demographic model. |
| `--cache1d`             | File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`. |
| `--cache2d`             | File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`. |
| `--pdf1d`               | 1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`. |
| `--pdf2d`               | 2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`. |
| `--ratio`               | Ratio for the nonsynonymous mutations to the synonymous mutations. |
| `--pdf-file`            | Name of python probability density function module file (not including .py) that contains custom probability density functions to use. Default: None. |
| `--p0`                  | Initial parameter values for inference. |
| `--output-prefix`       | Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files). |
| `--optimizations`       | Total number of optimizations to run. Default: 100. |
| `--check-convergence`   | Start checking for convergence after a chosen number of optimizations. Optimization runs will stop early if convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default. |
| `--force-convergence`   | Start checking for convergence after a chosen number of optimizations. Optimization runs will continue until convergence criteria is reached (--optimizations flag will be ignored). BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default. |
| `--work-queue`          | Enable Work Queue. Additional arguments are the WorkQueue project name, the name of the password file. |
| `--port`                | Choose a specific port for Work Queue communication. Default 9123. |
| `--debug-wq`            | Store debug information from WorkQueue to a file called "debug.log". Default: False. |
| `--maxeval`             | Max number of parameter set evaluations tried for optimizing demography. Default: Number of parameters multiplied by 100. |
| `--maxtime`             | Max amount of time for optimizing demography. Default: Infinite. |
| `--cpus`                | Number of CPUs to use in multiprocessing. Default: All available CPUs. |
| `--gpus`                | Number of GPUs to use in multiprocessing. Default: 0. |
| `--bestfit-p0-file`     | Pass in a .bestfit or .opt.<N> file name to cycle --p0 between up to the top 10 best fits for each optimization. |
| `--delta-ll`            | When using --check-convergence argument in InferDM or InferDFE modules or the BestFits module, set the max percentage difference for log-likliehoods compared to the best optimization log-likliehood to be consider convergent (with 1 being 100% difference to the best optimization's log-likelihood). Default: 0.0001. |
| `--model`               | Name of the demographic model. To check available demographic models, please use `dadi-cli Model`. |
| `--model-file`          | Name of python module file (not including .py) that contains custom models to use. Can be an HTML link. Default: None. |
| `--grids`               | Sizes of grids. Default: Based on sample size. |
| `--nomisid`             | Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized. |
| `--constants`           | Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None. |
| `--lbounds`             | Lower bounds of the optimized parameters. |
| `--ubounds`             | Upper bounds of the optimized parameters. |
| `--global-optimization` | Use global optimization before doing local optimization. Default: False. |
| `--seed`                | Random seed. |
