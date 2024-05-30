# Statistical testing

## Bootstrapped spectrum generation

To perform uncertainty analysis, `dadi` offers [an approach](https://dadi.readthedocs.io/en/latest/user-guide/uncertainty-analysis/) using the Godambe Information Matrix (GIM). To utilize this method, users should begin by using the `GenerateFs` subcommand to generate bootstrapped data from VCF files.

In this example, we generate `20` bootstraps using the `--bootstrap` argument to save time, though we recommend users perform `100` bootstraps for more robust results. The `--chunk-size` argument specifies the maximum length of the chromosome chunks, which are then randomly drawn with replacement to create the bootstrapped chromosomes. The `--output` argument sets the prefix for the output files and the directory where the allele frequency spectra from the bootstrapped chromosomes will be stored.

```
dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.syn.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.syn

dadi-cli GenerateFs --vcf examples/data/1KG.YRI.CEU.non.vcf.gz --pop-info examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.non
```

The output files from the above commands can be found in the `bootstrapping_syn` directory for synonymous SNPs and the `bootstrapping_non` directory for non-synonymous SNPs [here](https://github.com/xin-huang/dadi-cli/tree/revision/examples/results/fs). 

## Confidence interval estimation

After obtaining bootstrapped spetra, users can estimate the confidence intervals for the demographic or DFE parameters.

For our [demographic inference example](https://dadi-cli.readthedocs.io/en/revision/userguide/demog/), users can use the following command to estimate the confidence intervals for the demographic parameters:

```         
dadi-cli StatDM --fs examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs --model split_mig --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --grids 60 80 100 --bootstrapping-dir examples/results/fs/bootstrapping_syn/ --output examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demog.params.godambe.ci
```

For our [DFE inference example](https://dadi-cli.readthedocs.io/en/revision/userguide/dfe/), users can use the following command to estimate the confidence intervals for the 1D DFE parameters:

```         
dadi-cli StatDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --dfe-popt examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits --cache1d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl --pdf1d lognormal --bootstrapping-nonsynonymous-dir examples/results/fs/bootstrapping_non/ --bootstrapping-synonymous-dir examples/results/fs/bootstrapping_non/ --output examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci
```

These commands use the bootstrapped spectra to estimate the confidence intervals for the respective parameters, providing more robust and reliable inference results.

## Output

The results are stored in [1KG.YRI.CEU.20.split_mig.bestfit.demog.params.godambe.ci](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demog.params.godambe.ci) and [1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.1D_lognormal.params.godambe.ci), respectivly.

The 95% confidence intervals for the demographic parameters in our [demographic inference example](https://dadi-cli.readthedocs.io/en/revision/userguide/demog/) are shown below: 

```
Estimated 95% uncerts (theta adj), with step size 0.1): [0.0652234  0.01448371 0.02478827 0.07938722 0.00287734]
Lower bounds of 95% confidence interval : [2.16878752 0.50740874 0.26407614 1.13594438 0.01764644]
Upper bounds of 95% confidence interval : [2.29923431 0.53637617 0.31365269 1.29471882 0.02340113]

Estimated 95% uncerts (theta adj), with step size 0.01): [0.07667109 0.02254708 0.02647544 0.07385703 0.00264314]
Lower bounds of 95% confidence interval : [2.15733983 0.49934538 0.26238897 1.14147457 0.01788065]
Upper bounds of 95% confidence interval : [2.310682   0.54443953 0.31533986 1.28918863 0.02316693]

Estimated 95% uncerts (theta adj), with step size 0.001): [0.05868048 0.00972338 0.00409709 0.01693387 0.00291598]
Lower bounds of 95% confidence interval : [2.17533044 0.51216908 0.28476733 1.19839773 0.0176078 ]
Upper bounds of 95% confidence interval : [2.2926914  0.53161583 0.29296151 1.23226547 0.02343977]
```

Three different step sizes (0.1, 0.01, and 0.001) are tested when using the GIM. Ideally, 95% confidence intervals will be consistent across step sizes. For each step size:

- The first line shows the estimated uncertainty at the 95% confidence level.
- The second line provides the lower bounds of the 95% confidence intervals for each parameter. The parameters and their order match those in [1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits](examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits). The parameters are `nu1`, `nu2`, `T`, `m`, `misid`. For example, if the best fit value of `nu1` is `2.234010915680658` and the estimated uncertainty at the 95% confidence level with step size 0.1 for `nu1` is `0.0652234`, its lower bound is calculated as `2.234010915680658 - 0.0652234 = 2.16878752`.
- The third line shows the upper bounds of the 95% confidence intervals for each parameter.

For step size 0.1, the confidence intervals for each demographic parameters are:

| Parameter | 95% confidence interval |
| - | - |
| `nu1` | [2.16878752, 2.29923431] |
| `nu2` | [0.50740874, 0.53637617] |
| `T` | [0.26407614, 0.31365269] |
| `m` | [1.13594438, 1.29471882] |
| `misid` | [0.01764644, 0.02340113] |

## Arguments

### `StatDM`

| Argument | Description |
| - | - |
| `--fs` | Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link. |
| `--model` | Name of the demographic model. To check available demographic models, please use `dadi-cli Model`. |
| `--model-file` | Name of python module file (not including .py) that contains custom models to use. Can be an HTML link. Default: None. |
| `--grids` | Sizes of grids. Default: Based on sample size. |
| `--nomisid` | Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized. |
| `--output` | Name of the output file. |
| `--constants` | Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None. |
| `--eps` | Step sizes to try for Godambe analysis. Default: [0.1, 0.01, 0.001]. |
| `--demo-popt` | File contains the bestfit demographic parameters, generated by `dadi-cli BestFit`. |
| `--bootstrapping-dir` | Directory containing boostrapping spectra. |
| `--logscale` | Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False. |

### `StatDFE`

| Argument | Description |
| - | - |
| `--fs` | Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link. |
| `--cache1d` | File name of the 1D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`. |
| `--cache2d` | File name of the 2D DFE cache. To generate the cache, please use `dadi-cli GenerateCache`. |
| `--pdf1d` | 1D probability density function for the DFE inference. To check available probability density functions, please use `dadi-cli Pdf`. |
| `--pdf2d` | 2D probability density function for the joint DFE inference. To check available probability density functions, please use `dadi-cli Pdf`. |
| `--nomisid` | Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized. |
| `--output` | Name of the output file. |
| `--constants` | Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None. |
| `--eps` | Step sizes to try for Godambe analysis. Default: [0.1, 0.01, 0.001]. |
| `--dfe-popt` | File containing the bestfit DFE parameters, generated by `dadi-cli BestFit`. |
| `--bootstrapping-nonsynonymous-dir` | Directory containing boostrapping spectra. |
| `--bootstrapping-synonymous-dir` | Directory containing boostrapping spectra, required to adjust nonsynonymous theta for differences in synonymous theta. |
| `--logscale` | Determine whether estimating the uncertainties by assuming log-normal distribution of parameters; Default: False. |
