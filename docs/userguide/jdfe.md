# Joint DFE inference

## Inferring a bivariate lognormal joint DFE

Here we will infer a joint DFE with selection potentially being different in the two populations. We define the DFE as a bivariate lognormal distribution with `--pdf2d` and pass in a cache that assumes the population-scaled selection coefficients are different in the two populations through `--cache2d`. The bivariate lognormal has an extra parameter `rho`, the correlation of the DFE between the populations. We can allow `mu_log` and `sigma_log` be different or the same in our populations. `dadi-cli` will run either the symmetric (shared `mu_log` and `sigma_log`) or asymmetric (independent `mu_log` and `sigma_log`) bivariate lognormal based on the number of parameters. For the symmetric bivariate lognormal the parameters are `log_mu`, `log_sigma`, and `rho`, the asymmetric bivariate lognormal the parameters are `log_mu1`, `log_mu2`, `log_sigma1`, `log_sigma2`, and `rho`, where 1 denotes the first population and 2 denotes the second population.

An example of running a symmetrical bivariate lognormal is:

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 .5 .5 --lbounds -10 0.01 0.001 0 --ubounds 10 10 0.999 0.5 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_sym_lognormal.params --optimizations 15 --maxeval 400 --check-convergence
```

An example of running an asymmetrical bivariate lognormal is:

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_asym_lognormal.params --optimizations 10 --maxeval 400 --check-convergence
```

## Inferring mixture model joint DFE

Here, we will use a mixture of a univariate lognormal and a bivariate lognormal distribution. To make the mixture we pass in options for both 1D and 2D: `--pdf1d`, `--pdf2d`, `--cache1d`, and `--cache2d`. Because the mixture model is assuming some proportion of the DFE is lognormal and the other is bivariate, the bivariate is symmeteric. The parameters for the mixture lognormal DFE are `log_mu`, `log_sigma`, `rho`,and `w`, the proportional weight of the bivariate lognormal DFE (1-`w` would be the weight of the univariate lognormal distribution). In this example we fix `rho` of the bivariate component to 0 with the `--constants` option.

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --mix-pdf mixture_lognormal --p0 1 1 0 .5 .5 --lbounds -10 0.01 -1 0.001 0 --ubounds 10 10 -1 0.999 0.5 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 1 --maxeval 400 --check-convergence
```

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.split_mig.bestfit.demo.params`, the first column is the log-likelihood.

| likelihood | mu   | sigma | rho | w   | misidentification |
|------------|------|-------|-----|-----|-------------------|
| -1389      | 5.51 | 7.65  | 0   | 0   | 0.017             |
