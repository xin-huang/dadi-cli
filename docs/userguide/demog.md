# Demographic inference

## Model Parameters

The demographic models in dadi are distinguished from one another by the parameters that make them up. For most models, the main parameters are `nu`, population size change, and `T`, time.

`nu` is the population size relative to a reference population (the ancestral population or the effective population size). So a `nu` of 3 means the population is triple the size of the reference population, or \\(3 N_{\text{ref}}\\).

`T` is the time in \\(\text{ploidy} \cdot N_{\text{ref}}\\) generations. So for humans, time is in units of `T` are \\(2 N_{\text{ref}}\\)
In order to convert `T` into years, for diploids, users would use the conversion: \\(2 N_{\text{ref}} T\\)
To convert `T` into generations, users would divide years by generations per-year, ex. for Humans estimating 25 years per-generation: \\(\frac{2 N_{\text{ref}} T}{25 \text{ years per generation}}\\).

Each model inference will produce a \\(\theta\\) value, which is roughly a population scale neutral mutation rate. This value is important for estimating the DFE (see [dadi documentation](https://dadi.readthedocs.io/en/latest/user-guide/dfe-inference/) for more specific details) and calculating \\(N_\text{ref}\\), using the conversion \\(\frac{\theta}{4 \mu L}\\), where \\(\mu\\) is the genomic mutation rate and \\(L\\) is the length of sequence that could have ended up in the SNPs data. Put another way, \\(L\\) is the total length of the genome that was sequenced and could have been the same type of SNP (intergenic, synonymous, nonsynonymous) being analyized.

For demographic models with more than one population, `m`, the rate of migration, is an additional parameter that is common in dadi demographic models. It is common in dadi documentation to denote migration rate by `m`, then the destination population, followed by source population. For example, `m12` would translate to the rate of population 2 that migrants to population 1. `m` can be converted into units of fraction of inviduals in a destination population made up of a source population: \\(\frac{m}{2 N_{\text{ref}}}\\)

Another potential parameter users might infer is `misid`, the percentage of ancestral misidentification. If users' SNP data contains ancestral allele state (usually in the VCF, this will be denoted as AA= in the INFO column), dadi-cli can generate an unfolded alelle frequency spectrum by assuming the derived allele is the one not matching the ancestral state rather than assuming the derived allele is the one with the lower population frequency. This results in a more SNPs that are shared in more of the population. `misid` corrects for model assumptions that SNPs with high population prevelance are rarer.

The final parameter that common in dadi models is `F`, the percentage of inbreeding in the population. A common sign of inbreeding in populations is more provalence of homozygotic SNPs, resulting in higher than expected SNPs with an even number of sample. See dadi's documentation on [inbreeding](https://dadi.readthedocs.io/en/latest/user-guide/inbreeding/) for more details.

## Input

After obtaining the allele frequency spectrum, we can infer a demographic model from the spectrum for synonymous SNPs (e.g., [1KG.YRI.CEU.20.syn.unfolded.fs](https://github.com/xin-huang/dadi-cli/blob/master/examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs)), because we usually assume synonymous SNPs are neutral. Intergenic SNPs are an alternative for data under neutral selection. Here, we use the `split_mig` model:

![split_mig](https://github.com/xin-huang/dadi-cli/blob/revision/docs/figs/split_mig.png?raw=true)

In this model, the ancestral population diverges into two populations, which then have an instantaneous change of population size with migration between the two populations over time. Hence, we have four parameters and can use the following command for fitting the demographic model:

```
dadi-cli InferDM --fs examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5 --output-prefix examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params --optimizations 10 --cpus 2
```

To see descriptions of the four parameters in the `split_mig` model, users can use:

```
dadi-cli Model --names split_mig
```

which returns:

```
- split_mig:

        params = (nu1,nu2,T,m)

        Split into two populations of specifed size, with migration.

        nu1: Size of population 1 after split.
        nu2: Size of population 2 after split.
        T: Time in the past of split (in units of 2*Na generations)
        m: Migration rate between populations (2*Na*m)
```

By default, with unfolded data an additional parameter is added, which quantifies the proportion of sites for which the ancestral state was misidentified (to disable this, the `--nomisid` option can be specified). Therefore, we have five parameters in total: `nu1`, `nu2`, `T`, `m`, `misid`.

`--lbounds` and `--ubounds` set the lower and upper boundaries, respectively, for the model parameters during inference. Establishing these boundaries prevents optimizers from going into parameter spaces that are difficult for `dadi` to calculate, such as low population size, high time, and high migration. In this case, we set the range of relative population sizes to be explored as 1e-3 to 100, the range of divergence time to 0 to 1, the range of migration rates from 0 to 10, and the range of misidentification proportions to 0 to 0.5. 

`dadi-cli` will by default calculate starting parameters between the boundaries, but users can specify starting parameters with `--p0`. Parameters can be fixed to certain values with `--constants`. If a parameter value passed into `--constants` is `-1`, it will not be fixed to a value. 

Because we need to run optimization several times to find a converged result with maximum likelihood, we use `--optimizations` to specify how many times the optimization will run. 

`dadi-cli` can use multiprocessing to run optimizations in parallel and by default the max number of CPUs available will be utilized. If users want fewer CPUs to be used, they can use the `--cpus` option to pass in the number of CPUs they want utilized for multiprocessing. If GPUs are available, they can be used by passing the `--gpus` option with the number of GPUs to be used.

## Output

After the optimization, a file [1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0) will be made. Any subsequent optimzations using the same output argument will be number `.1`, `.2`, etc.

The results in [1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0) are as follows:

```
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDM --fs examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5 --output-prefix examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params --optimizations 10 --cpus 2
# Log(likelihood)       nu1     nu2     T       m       misid   theta
-1363.2200840259638     2.2270712838611826      0.5216637414533595      0.28707487206148485     1.2124631528233945      0.020437855404645933    6804.072401672313
-1470.5333431072556     1.9662096210813453      0.6035362171867105      0.46423214235747146     1.3147455119553204      0.01757407083077342     6231.485409395597
-2919.374066741771      0.42018671284017167     0.0756545735822522      1.0     10.0    0.0     23511.32160786105
-2919.3740667456673     0.4201864967660094      0.07565463514964295     1.0     10.0    0.0     23511.317066913223
-1366.11680798408       2.326822899078075       0.519968511745911       0.27519836239929885     1.17032575627153        0.020328937284166793    6812.277737041025
-1364.3007967766132     2.1581920217695116      0.5154897444630471      0.29669890435293783     1.2675575809660455      0.02036332864923114     6811.884146976314
-1363.1760448023297     2.234010915680658       0.5218924552311363      0.2888644164114447      1.2153316011346929      0.020523786229611048    6792.834074186963
-1363.2675966704428     2.2049347529056105      0.5220521286638555      0.29578720506141454     1.2375478474168402      0.020477244062454117    6778.545189390314
-1556.5440465916327     2.269229841357405       0.6000476636552503      0.9817413122334883      1.3599101120794626      0.029327213821618615    5209.335687633874
-2919.3740667483544     0.4201870261583265      0.07565453551901934     1.0     9.999999999999998       0.0     23511.320211309674
```

The first line of the header records the command and parameters that were used to generate the results.

The second line of the header describes the meaning of each column:

- The first column represents the likelihood of the model in log scale.
- The last column indicates the population-scale mutation rate.
- The second to last column contains the parameter for ancestral allele misidentification. If `--nomisid` is used, this column will not be present.
- The remaining columns detail the demographic parameters corresponding to the model specified by `--model`. Different demographic models will have different parameters. To understand their order and meaning, please use `dadi-cli Model`.

Since we perform 10 optimizations, this file contains 10 rows, with each row recording the results from an individual optimization.

Users can further use the `BestFit` command to obtain the best fit parameters across all optimization runs with a matching prefix.

```         
dadi-cli BestFit --input-prefix examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
```

The result is in a file [1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits). This file contains the 100 highest likelihood parameter sets found (if at least that many optimizations have been carried out). If optimization converged, then the file also contains the converged results.

The results look like:

```
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli BestFit --input-prefix examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDM --fs examples/results/fs/1KG.YRI.CEU.20.syn.unfolded.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5 --output-prefix examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params --optimizations 10 --cpus 2
#
# Converged results
# Log(likelihood)	nu1	nu2	T	m	misid	theta
-1363.1760448023297	2.234010915680658	0.5218924552311363	0.2888644164114447	1.2153316011346929	0.020523786229611048	6792.834074186963
-1363.2200840259638	2.2270712838611826	0.5216637414533595	0.28707487206148485	1.2124631528233945	0.020437855404645933	6804.072401672313
-1363.2675966704428	2.2049347529056105	0.5220521286638555	0.29578720506141454	1.2375478474168402	0.020477244062454117	6778.545189390314
#
# Top 100 results
# Log(likelihood)	nu1	nu2	T	m	misid	theta
-1363.1760448023297	2.234010915680658	0.5218924552311363	0.2888644164114447	1.2153316011346929	0.020523786229611048	6792.834074186963
-1363.2200840259638	2.2270712838611826	0.5216637414533595	0.28707487206148485	1.2124631528233945	0.020437855404645933	6804.072401672313
-1363.2675966704428	2.2049347529056105	0.5220521286638555	0.29578720506141454	1.2375478474168402	0.020477244062454117	6778.545189390314
-1364.3007967766132	2.1581920217695116	0.5154897444630471	0.29669890435293783	1.2675575809660455	0.02036332864923114	6811.884146976314
-1366.11680798408	2.326822899078075	0.519968511745911	0.27519836239929885	1.17032575627153	0.020328937284166793	6812.277737041025
-1470.5333431072556	1.9662096210813453	0.6035362171867105	0.46423214235747146	1.3147455119553204	0.01757407083077342	6231.485409395597
-1556.5440465916327	2.269229841357405	0.6000476636552503	0.9817413122334883	1.3599101120794626	0.029327213821618615	5209.335687633874
-2919.374066741771	0.42018671284017167	0.0756545735822522	1.0	10.0	0.0	23511.32160786105
-2919.3740667456673	0.4201864967660094	0.07565463514964295	1.0	10.0	0.0	23511.317066913223
-2919.3740667483544	0.4201870261583265	0.07565453551901934	1.0	9.999999999999998	0.0	23511.320211309674
```

When using `BestFit`, users can adjust the criteria for convergence. By default, optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.01% units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option and passing in the percentage difference in decimal form (so the default is 0.0001, rather than 0.01). Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used (for example, the sample size can have a big effect on the size of the log-likelihood). Optimizations in the bestfit file will be ordered by log-likelihood and should be examined closely for similarity of parameter values in convergent fits.

If users have experience with the data they are using, they can use the `--check-convergence` or `--force-convergence` option in `InferDM`. The `--check-convergence` option will run `BestFit` after a specified number of optimizations to check for convergence and stop running optimizations if convergence is reached. For example, `--check-convergence 10` will run 10 optimizations and then start checking for convergence. Optimization runs will stop before the requested number of `--optimizations` if convergence is met. The `--force-convergence` option will constantly add new optimization runs until convergence is reached, ignoring `--optimization`. When using `--check-convergence` or `--force-convergence` users can also use `--delta-ll` to change the convergence criteria. Sometimes, the best fit parameters may be close to the boundaries. Users should be cautious and test increasing the boundaries to examine whether these boundaries would affect the results significantly.

Because there is randomness built into `dadi-cli` for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can also try to use a global optimization before moving onto the local optimization with the `--global-optimization` option. 25% of the number of optimizations the user passes in will be used for the global optimization and the remaining will be used for the local optimization. Additionally, users can use the output files from `InferDM` or `BestFit` as a starting point for the inital parameters with the `--bestfit-p0-file` flag and passing in the file they want to use. The starting parameters will be randomly chosen from the top ten fits and perturbed.

Finally, the grid sizes may also affect the inference. If `n` is the maximum of the sample sizes, then the default grid sizes are `(int(n*1.1)+2, int(n*1.2)+4, int(n*1.3)+6)`.

## Arguments

| Argument | Description |
| - | - |
| `--fs`                  | Frequency spectrum of mutations used for inference. To generate the frequency spectrum, please use `dadi-cli GenerateFs`. Can be an HTML link. |
| `--p0`                  | Initial parameter values for inference. |
| `--output-prefix`       | Prefix for output files, which will be named <output_prefix>.InferDM.opts.<N>, where N is an increasing integer (to avoid overwriting existing files). |
| `--optimizations`       | Total number of optimizations to run. Default: 100. |
| `--check-convergence`   | Start checking for convergence after a chosen number of optimizations. Optimization runs will stop early if convergence criteria are reached. BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default. |
| `--force-convergence`   | Start checking for convergence after a chosen number of optimizations. Optimization runs will continue until convergence criteria is reached (--optimizations flag will be ignored). BestFit results file will be call <output_prefix>.InferDM.bestfits. Convergence not checked by default. |
| `--work-queue`          | Enable Work Queue. Additional arguments are the WorkQueue project name, the name of the password file. |
| `--port`                | Choose a specific port for Work Queue communication. Default 9123. |
| `--debug-wq`            | Store debug information from WorkQueue to a file called "debug.log". Default: False. |
| `--maxeval`             | Max number of parameter set evaluations tried for optimization. Default: Number of parameters multiplied by 100. |
| `--maxtime`             | Max amount of time for optimization. Default: Infinite. |
| `--cpus`                | Number of CPUs to use in multiprocessing. Default: All available CPUs. |
| `--gpus`                | Number of GPUs to use in multiprocessing. Default: 0. |
| `--bestfit-p0-file`     | Pass in a .bestfit or .opt.<N> file name to cycle --p0 between up to the top 10 best fits for each optimization. |
| `--delta-ll`            | When using --check-convergence argument in InferDM or InferDFE modules or the BestFits module, set the max percentage difference for log-likliehoods compared to the best optimization log-likliehood to be consider convergent (with 1 being 100% difference to the best optimization's log-likelihood). Default: 0.0001. |
| `--model`               | Name of the demographic model. To check available demographic models, please use `dadi-cli Model`. |
| `--model-file`          | Name of python module file (not including .py) that contains custom models to use. Can be an HTML link. Default: None. |
| `--grids`               | Sizes of grids. Default: Based on sample size. |
| `--nomisid`             | Enable to *not* include a parameter modeling ancestral state misidentification when data are polarized. |
| `--coverage-model`      | Enable coverage model. Arguments are: 1. The name of the <>.coverage.pickle file produced by GenerateFs --calc-coverage. 2. The total number of samples sequenced for each population in the VCF. |
| `--coverage-inbreeding` | Pass in optional population inbreeding parameters for the coverage model. |
| `--constants`           | Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None. |
| `--lbounds`             | Lower bounds of the optimized parameters. |
| `--ubounds`             | Upper bounds of the optimized parameters. |
| `--global-optimization` | Use global optimization before doing local optimization. Default: False. |
| `--seed`                | Random seed. |
