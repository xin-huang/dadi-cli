---
output:
  html_document: default
  pdf_document: default
---
# dadi-cli

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE) [![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/) [![build Status](https://github.com/xin-huang/dadi-cli/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/xin-huang/dadi-cli/actions) [![codecov](https://codecov.io/gh/xin-huang/dadi-cli/branch/master/graph/badge.svg?token=GI66f4R3RF)](https://codecov.io/gh/xin-huang/dadi-cli)

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data. However, using `dadi` requires knowledge of python and patience to tune different models.

## Installation

To install `dadi-cli`, users should clone this repo and use the following command

```         
python setup.py install
```

To get help information, users can use

```         
dadi-cli -h
```

There are nine subcommands in `dadi-cli`: - `GenerateFs` - `GenerateCache` - `InferDM` - `InferDFE` - `BestFit` - `Stat` - `Plot` - `Model` - `Pdf`

To display help information for each subcommand, users can use `-h`. For example,

```         
dadi-cli GenerateFs -h
```

## The workflow

## Usage: An Example

Here we use the data from the 1000 Genomes Project to demonstrate how to apply `dadi-cli` in research.

### Generating allele frequency spectrum from VCF files

`dadi-cli` only accepts VCF files to generate allele frequency spectra. To generate a spectrum, users can use

```         
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs

dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs
```

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

```         
NA12718 CEU
NA12748 CEU
NA12775 CEU
NA19095 YRI
NA19096 YRI
NA19107 YRI
```

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haplotypes for YRI and CEU respectively. We use a lower sample size here, because it allows us to speed up examples.

By default, `dadi-cli` generates folded spectra. To generate unfolded spectra, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

While making the spectrum, users can also mask the singleton calls that are exclusive to the population(s) with `--mask-singleton` or mask the exclusive and shared singleton calls with `--mask-singleton-shared`.

### Inferring demographic models

In this example, we infer a demographic model from the spectrum for synonymous SNPs. Here, we use the `split_mig` model. In this model, the ancestral population diverges into two populations, which then have an instantaneous change of population size with migration between the two populations over time. To see descriptions of the four parameters of the `split_mig` model, use `dadi-cli Model --names split_mig`. By default, with unfolded data an additional parameter is added, which quantifies the proportion of sites for which the ancestral state was misidentified. (To disable this, use the `--nomisid` option.) Therefore, we have five parameters in total.

To start the inference, users should specify the lower bounds and upper bounds for these parameters with `--lbounds` and `--ubounds`. For demographic models, setting parameter boundaries prevents optimizers from going into parameter spaces that are hard for `dadi` to calculate, such as low population size, high time, and high migration. In this case, we set the range of relative population sizes to be explored as 1e-3 to 100, the range of divergence time to 0 to 1, the range of migration rates from 0 to 10, and the range of misidentification proportions to 0 to 0.5. (Parameters can be fixed to certain values with `--constants`. In that case, `-1` indicates that a parameter is free to vary.) Because we need to run optimization several times to find a converged result with maximum likelihood, we use `--optimizations` to specify how many times the optimization will run. `dadi-cli` can use multiprocessing to run optimizations in parallel and by default the max number of CPUs available will be utilized. If users want fewer CPUs to be used, they can use the `--cpus` option to pass in the number of CPUs they want utilized for multiprocessing. If GPUs are available, they can be used by passing the `--gpus` option with the number of GPUs to be used.

<!--- As well, because our 1000 Genomes data is fairly large we can increase the maximum number of parameter sets each optimization will use with `--maxeval` and use our own grid points with `--grids`. -->

```         
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5  --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 10
```

After the optimization, a file `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.opts.0` will be made. Any subsequent optimzations using the same output argument will be number `.1`, `.2`, etc.

Users can use `BestFit` to obtain the best fit parameters across all optimization runs with a matching prefix.

```         
dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
```

The result is in a file `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits`. This file contains the 100 highest likelihood parameter sets found (if at least that many optimizations have been carried out). If optimization converged, then the file also contains the converged results.

The results look like:

```         
# /Users/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5
# /Users/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 10 --maxeval 200
#
# Converged results
# Log(likelihood)   nu1 nu2 T   m   misid   theta
-1358.656798384051  2.1981613475071864  0.5158391424566413  0.28524739475343264 1.2375756394365451  0.020683288489282133    6771.157432134759
-1358.6880947964542 2.196984200820028   0.5133914664638932  0.28277200202566527 1.2413354976672208  0.020632166672609045    6786.9015918739915
-1358.6985706673254 2.193829701862104   0.5150503581819097  0.28755609071963395 1.2477300697512446  0.020689738141788896    6765.701504724712
-1358.7339671606906 2.215035226792488   0.5170682238957518  0.2855564758596486  1.2327369856712844  0.02071860093359053 6759.1696821323685
#
# Top 100 results
# Log(likelihood)   nu1 nu2 T   m   misid   theta
-1358.656798384051  2.1981613475071864  0.5158391424566413  0.28524739475343264 1.2375756394365451  0.020683288489282133    6771.157432134759
-1358.6880947964542 2.196984200820028   0.5133914664638932  0.28277200202566527 1.2413354976672208  0.020632166672609045    6786.9015918739915
-1358.6985706673254 2.193829701862104   0.5150503581819097  0.28755609071963395 1.2477300697512446  0.020689738141788896    6765.701504724712
-1358.7339671606906 2.215035226792488   0.5170682238957518  0.2855564758596486  1.2327369856712844  0.02071860093359053 6759.1696821323685
-1358.9273502384722 2.2161166322584114  0.5192238541188319  0.2805756463060831  1.211174886229439   0.020776317690376894    6774.695201641862
-1359.391018756372  2.2144196583672064  0.5133883753095932  0.2936398676168146  1.2635603043453991  0.021378007902017316    6734.565951708204
-1370.3128577096236 2.2965153967334837  0.5252579237019416  0.3301972600288801  1.2726527078754761  0.021832076042802986    6531.457050865405
-1437.4626671227088 2.348110308415506   0.6039083548424201  0.456754335717111   1.2524206835381557  0.030106689556776402    5971.036610931144
-1591.7611157189594 1.9723568097803748  0.5074933640133197  0.9819908721498116  1.6576780338511465  0.024964816092429044    5651.0110782323845
-2008.8420038152385 4.223980226535977   0.7590647581822983  0.2679298140727045  0.7488053157919355  0.01757046441838214 5977.616341188507A
```

Because there is randomness built into dadi-cli for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can also try to use a global optimization before moving onto the local optimization with the `--global-optimization` option. 25% of the number of optimizations the user passes in will be used for the global and the remaining will be used for the local optimization.

Using `BestFit`, users can adjust the criteria for convergence. By default optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.01% units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option and passing in the percentage difference in decimal form (so the default is 0.0001, rather than 0.01). Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used (especially the sample size can effect the size of the log-likelihood). Optimizations in the bestfit file will be ordered by log-likelihood and should be examined closely for similarity of parameter values in convergent fits.

Finally, if you have experience with the data you are using, you can use the `--check-convergence` or `--force-convergence` option in `InferDM`. The `--check-convergence` option will run `BestFit` after each optimization to check for convergence and stop running optimizations once convergence is reached. The `--force-convergence` option will constantly add new optimization runs until convergence is reached. When using `--check-convergence` or `--force-convergence` you can pass in a value with `--delta-ll` as well to change the convergence criteria.

Sometimes parameters may be close to the boundaries. Users should be cautious and test increasing the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown below mirroring the bestfits file. The first column is the log-likelihood, then the corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| log-likelihood | nu1 | nu2  | T    | m    | misid | theta |
|----------------|-----|------|------|------|-------|-------|
| -1358.66       | 2.2 | 0.52 | 0.29 | 1.24 | 0.021 | 6772  |

### Generating caches for DFE inference

After inferring a best fit demographic model, users may also infer distributions of fitness effects (DFEs) from data. To perform DFE inference, users need to first generate of cache of frequency spectra. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel` model or the `split_mig_sel_single_gamma` model. The `split_mig_sel` model is used for inferring the DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. `--cpus 2` indicates that the computation will use 2 CPUs. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are the same in the two populations. If you want to to make the cache for the situation where the selection coefficients are independent from one another, use the `--dimensionality 2` option. You can use the `--gamma-bounds` option to choose the range of the gamma distribution and the `--gamma-pts` option can be used to specify the number of selection coefficients that will be selected in that range to generate your cache. Note that the higher (more negative) you make the `--gamma-bounds`, the bigger the grid points you will want to use.

```         
dadi-cli GenerateCache --model split_mig_sel_single_gamma --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cpus 4

dadi-cli GenerateCache --model split_mig_sel --dimensionality 2 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --cpus 4
```

### User defined demographic models

Users can also import their own models into dadi-cli. In the `examples/data` folder, there is a file `split_mig_fix_T_models.py` which has a custom demographic model and demographic models with selection. The file imports various functions from dadi that are used to build demographic models.

```         
from dadi import Numerics, Integration, PhiManip, Spectrum
```

Then defines the demographic model:

```         
def split_mig_fix_T(params, ns, pts):
    """
    Instantaneous split into two populations of specified size, with symmetric migration and a fixed time point.
    """
    nu1,nu2,m = params

    xx = Numerics.default_grid(pts)

    phi = PhiManip.phi_1D(xx)
    phi = PhiManip.phi_1D_to_2D(xx, phi)

    phi = Integration.two_pops(phi, xx, 0.3, nu1, nu2, m12=m, m21=m)

    fs = Spectrum.from_phi(phi, ns, (xx,xx))
    return fs
```

dadi-cli checks models for the names and number of parameters, so after defining the demographic model we add an attribute for a list of the parameter names:

```         
split_mig_fix_T.__param_names__ = ['nu1', 'nu2', 'm']
```

If you want to preform a DFE inference, you will need to add `gamma` parameters for `gamma` arguments when initializing $\phi$, ex:

```         
dadi.PhiManip.phi_1D(xx, gamma=gamma_Pop1)
```

And for integration steps, ex:

```         
dadi.Integration.two_pops(phi, xx, T, nu1, nu2, m12=m, m21=m, gamma1=gamma_Pop1, gamma2=gamma_Pop2)
```

When making your demographic models with selection and setting the inital $\phi$, take care to consider which population is is the ancestral population for the gamma argument in `dadi.PhiManip.phi_1D`.

Because custom model files can have multiple models in them, users will still want to use `--model` to pass in the model for demographic inference and cache generation. Here are some quick examples for users to run:

```         
dadi-cli InferDM --model split_mig_fix_T --model-file examples/data/split_mig_fix_T_models --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --p0 2 0.5 1.2 .02 --ubounds 3 1 2 0.03 --lbounds 1 1e-1 1e-1 1e-3 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params --optimizations 20 --maxeval 300 --check-convergence

dadi-cli GenerateCache --model split_mig_fix_T_one_s --model-file examples/data/split_mig_fix_T_models --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_one_s_psudo_new_model.spectra.bpkl --cpus 4

dadi-cli GenerateCache --model split_mig_fix_T_sel --model-file examples/data/split_mig_fix_T_models --dimensionality 2 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig_fix_T.demo.params.InferDM.bestfits --sample-size 20 20 --grids 160 180 200 --gamma-pts 10 --gamma-bounds 1e-4 20 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_psudo_new_model.spectra.bpkl --cpus 4
```

### Inferring DFE

For inferring the DFE, we fit the spectrum from nonsynonymous SNPs. Although our data come from two populations, we will first infer a one-dimensional DFE, which assumes that selection coefficients are equal in the two populations. We define the marginal DFE as a lognormal distribution with `--pdf1d`. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. Our parameters are `log_mu` the mean of the lognormal distribution, `log_sigma` the standard deviation of the lognormal distribution, and `misid`.

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence
```

The result is

```         
# /home/u25/tjstruck/miniconda3/bin/dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds 0 0.01 0 --ubounds 10 10 1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence
# /home/u25/tjstruck/miniconda3/bin/dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds 0 0.01 0 --ubounds 10 10 1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence
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

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.split_mig.bestfit.demo.params`, the first column is the log-likelihood followed by the parameters.

| likelihood | mu  | sigma | misidentification |
|------------|-----|-------|-------------------|
| -1389      | 5.5 | 7.6   | 0.017             |

### Inferring a bivariate lognormal joint DFE

Here we will infer a joint DFE with selection potentially being different in the two populations. We define the DFE as a bivariate lognormal distribution with `--pdf2d` and pass in a cache that assumes the population-scaled selection coefficients are different in the two populations through `--cache2d`. The bivariate lognormal has an extra parameter `rho`, the correlation of the DFE between the populations. We can allow `mu_log` and `sigma_log` be different or the same in our populations. `dadi-cli` will run either the symmetric (shared `mu_log` and `sigma_log`) or asymmetric (independent `mu_log` and `sigma_log`) bivariate lognormal based on the number of parameters. For the symmetric bivariate lognormal the parameters are `log_mu`, `log_sigma`, and `rho`, the asymmetric bivariate lognormal the parameters are `log_mu1`, `log_mu2`, `log_sigma1`, `log_sigma2`, and `rho`, where 1 denotes the first population and 2 denotes the second population.

An example of running a symmetrical bivariate lognormal is:

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 .5 .5 --lbounds -10 0.01 0.001 0 --ubounds 10 10 0.999 0.5 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_sym_lognormal.params --optimizations 15 --maxeval 400 --check-convergence
```

An example of running an asymmetrical bivariate lognormal is:

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.bivariate_asym_lognormal.params --optimizations 10 --maxeval 400 --check-convergence
```

### Inferring mixture model joint DFE

Here, we will use a mixture of a univariate lognormal and a bivariate lognormal distribution. To make the mixture we pass in options for both 1D and 2D: `--pdf1d`, `--pdf2d`, `--cache1d`, and `--cache2d`. Because the mixture model is assuming some proportion of the DFE is lognormal and the other is bivariate, the bivariate is symmeteric. The parameters for the mixture lognormal DFE are `log_mu`, `log_sigma`, `rho`,and `w`, the proportional weight of the bivariate lognormal DFE (1-`w` would be the weight of the univariate lognormal distribution). In this example we fix `rho` of the bivariate component to 0 with the `--constants` option.

```         
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --mix-pdf mixture_lognormal --p0 1 1 0 .5 .5 --lbounds -10 0.01 -1 0.001 0 --ubounds 10 10 -1 0.999 0.5 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 1 --maxeval 400 --check-convergence
```

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.split_mig.bestfit.demo.params`, the first column is the log-likelihood.

| likelihood | mu   | sigma | rho | w   | misidentification |
|------------|------|-------|-----|-----|-------------------|
| -1389      | 5.51 | 7.65  | 0   | 0   | 0.017             |

### Performing statistical testing

To performing statistical testing with the Godambe Information Matrix (GIM), users should first use `GenerateFs` to generate bootstrapping data from VCF files. In this example we generate 20 bootstraps to save on time, but we recommend users do 100. `--chunk-size` is the max length of chunks the chromosomes will be broken up into and used to randomly draw from with replacement to make our bootstrapped chromosomes.

```         
dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold

dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold
```

To estimate the confidence intervals for the demographic parameters, users can use

```         
dadi-cli StatDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --grids 60 80 100 --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci
```

To estimate the confidence intervals for the joint DFE parameters, users can use

```         
dadi-cli StatDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --bootstrapping-nonsynonymous-dir ./examples/results/fs/bootstrapping_non/ --bootstrapping-synonymous-dir ./examples/results/fs/bootstrapping_non/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci
```

Three different step sizes are tested when using the GIM. Ideally 95% confidence intervals will be consistent between step sizes.

### Plotting

`dadi-cli` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.unfold.fs.pdf --model split_mig

dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs.pdf --model split_mig
```

To compare two frequency spectra from data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --fs2 ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf --model None
```

To compare frequency spectra between a demographic model without selection and data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.vs.split_mig.pdf --model split_mig
```

To compare frequency spectra between a demographic model with selection and data, users can use

```         
dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --model split_mig --pdf1d lognormal --pdf2d biv_lognormal --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.vs.lognormal_mixture.pdf
```

By default, `dadi-cli` projects the sample size down to 20 for each population. Users can use `--projections` to lower the sample size for visualization purposes.

### Using Work Queue for distributed inference with dadi-cli

`dadi-cli` `InferDM` and `InferDFE` has built in options to work with Cooperative Computing Tools (`CCTools`)'s `Work Queue` for launching independent optimizations across multiple machines. To use Work Queue, users can use conda to install the required packages:

``` bash
conda install -c conda-forge dill ndcctools
```

This example has been tested for submitting jobs to a `Slurm Workload Manager`. First we want to submit a factory.

```bash
work_queue_factory -T local -M dm-inference -P ./tests/mypwfile --workers-per-cycle=0 --cores=1
```

`dm-inference` is the project name and `mypwfile` is a file containing a password, both of which are needed for `dadi-cli` use. Next you'll want to submit jobs from `dadi-cli`.

```bash
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.work_queue.params --optimizations 5 --maxeval 200 --check-convergence --work-queue dm-inference ./tests/mypwfile
```

`dadi-cli` will send the number of workers as the number of optimizations you request. The `check-convergence` and `force-convergence` options work with `Work Queue` as well.

### Available demographic models

`dadi-cli` provides a subcommand `Model` to help users finding available demographic models in `dadi`. To find out available demographic models, users can use

```         
dadi-cli Model --names
```

Then the available demographic models will be displayed in the screen:

```         
Available 1D demographic models:
- bottlegrowth_1d
- growth
- snm_1d
- three_epoch
- two_epoch

Available 2D demographic models:
- bottlegrowth_2d
- bottlegrowth_split
- bottlegrowth_split_mig
- IM
- IM_pre
- split_mig
- split_asym_mig
- snm_2d

Available demographic models with selection:
- equil
- equil_X
- IM_sel
- IM_sel_single_gamma
- IM_pre_sel
- IM_pre_sel_single_gamma
- split_mig_sel
- split_mig_sel_single_gamma
- split_asym_mig_sel
- split_asym_mig_sel_single_gamma
- two_epoch_sel
- three_epoch_sel
```

To find out the parameters and detail of a specific model, users can use the name of the demograpic model as the parameter after `--names`. For example,

```         
dadi-cli Model --names split_mig
```

Then the detail of the model will be displayed in the screen:

```         
- split_mig:

        Split into two populations of specifed size, with symmetric migration.
        Two populations in this model.

        params = [nu1,nu2,T,m]

            nu1: Size of population 1 after split (in units of Na)
            nu2: Size of population 2 after split (in units of Na)
              T: Time in the past of split (in units of 2*Na generations)
              m: Migration rate between populations (2*Na*m)
```

### Available DFE distributions

`dadi-cli` provides a subcommand `Pdf` to help users finding available probability density functions for DFE inference in `dadi`.

To find out available probability density functions, users can use

```         
dadi-cli Pdf --names
```

Then the availalbe functions will be displayed in the screen:

```         
Available probability density functions:
- beta
- biv_ind_gamma
- biv_lognormal
- exponential
- gamma
- lognormal
- normal
- mixture
```

To find out the parameters and the detail of a specific function, users can use the name of the function as the parameter after `--names`. For example,

```         
dadi-cli Pdf --names lognormal
```

Then the detail of the function will be displayed in the screen:

```         
- lognormal:

        Lognormal probability density function.

        params = [log_mu, log_sigma]
```

## Dependencies

-   [dadi \>2.1.0](https://bitbucket.org/gutenkunstlab/dadi/src/master/)

## References

1.  [Gutenkunst et al., *PLoS Genet*, 2009.](http://doi.org/10.1371/journal.pgen.1000695)
2.  [Huang et al., *Mol Biol Evol*, 2021.](https://doi.org/10.1093/molbev/msab162)
