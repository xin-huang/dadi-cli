# Demographic inference

## Input

In this example, we infer a demographic model from the spectrum for synonymous SNPs, because we usually assume synonymous SNPs are neutral. Users can specify a demographic model inferred with the `--model` subcommand. Here, we use the `split_mig` model. In this model, the ancestral population diverges into two populations, which then have an instantaneous change of population size with migration between the two populations over time. To see descriptions of the four parameters of the `split_mig` model, use `dadi-cli Model --names split_mig`. By default, with unfolded data an additional parameter is added, which quantifies the proportion of sites for which the ancestral state was misidentified. (To disable this, use the `--nomisid` option.) Therefore, we have five parameters in total: `nu1`, `nu2`, `T`, `m`, `misid`.

To start the inference, users should specify the boundaries for the model parameters with `--lbounds` and `--ubounds`. For demographic models, setting parameter boundaries prevents optimizers from going into parameter spaces that are hard for `dadi` to calculate, such as low population size, high time, and high migration. In this case, we set the range of relative population sizes to be explored as 1e-3 to 100, the range of divergence time to 0 to 1, the range of migration rates from 0 to 10, and the range of misidentification proportions to 0 to 0.5. `dadi-cli` will by default calculate starting parameters between the boundaries, but users can specify starting parameters with `--p0`. Parameters can be fixed to certain values with `--constants`. If a parameter value passed into `--constants` is `-1`, it will not be fixed to a value. Because we need to run optimization several times to find a converged result with maximum likelihood, we use `--optimizations` to specify how many times the optimization will run. `dadi-cli` can use multiprocessing to run optimizations in parallel and by default the max number of CPUs available will be utilized. If users want fewer CPUs to be used, they can use the `--cpus` option to pass in the number of CPUs they want utilized for multiprocessing. If GPUs are available, they can be used by passing the `--gpus` option with the number of GPUs to be used.


```
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5  --output ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params --optimizations 10
```

Please make sure the directory `./examples/results/demog/` exist before running the above command.

## Output

After the optimization, a file `./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.opts.0` will be made. Any subsequent optimzations using the same output argument will be number `.1`, `.2`, etc.

Users can use `BestFit` to obtain the best fit parameters across all optimization runs with a matching prefix.

```         
dadi-cli BestFit --input-prefix ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
```

The result is in a file `./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits`. This file contains the 100 highest likelihood parameter sets found (if at least that many optimizations have been carried out). If optimization converged, then the file also contains the converged results.

The results look like:

```         
# /Users/user/anaconda3/envs/dadicli/bin/dadi-cli BestFit --input-prefix ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5
# /Users/user/anaconda3/envs/dadicli/bin/dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --lbounds 1e-3 1e-3 0 0 0 --ubounds 100 100 1 10 0.5  --output ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params --optimizations 10
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

## Settings

Because there is randomness built into `dadi-cli` for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can also try to use a global optimization before moving onto the local optimization with the `--global-optimization` option. 25% of the number of optimizations the user passes in will be used for the global optimization and the remaining will be used for the local optimization.

When using `BestFit`, users can adjust the criteria for convergence. By default optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.01% units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option and passing in the percentage difference in decimal form (so the default is 0.0001, rather than 0.01). Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used (for example, the sample size can have a big effect on the size of the log-likelihood). Optimizations in the bestfit file will be ordered by log-likelihood and should be examined closely for similarity of parameter values in convergent fits.

Finally, if users have experience with the data they are using, they can use the `--check-convergence` or `--force-convergence` option in `InferDM`. The `--check-convergence` option will run `BestFit` after a specified number of optimizations to check for convergence and stop running optimizations if convergence is reached. For example, `--check-convergence 10` will run 10 optimizations and then start checking for convergence. Optimization runs will stop before the requested number of `--optimizations` if convergence is met. The `--force-convergence` option will constantly add new optimization runs until convergence is reached, ignoring `--optimization`. When using `--check-convergence` or `--force-convergence` users can also use `--delta-ll` to change the convergence criteria. Users can use the output files from `InferDM` or `BestFit` as a starting point for the inital parameters with the `--bestfit-p0-file` flag and passing in the file they want to use. The starting parameters will be randomly chosen from the top ten fits and perturbed.

Sometimes parameters may be close to the boundaries. Users should be cautious and test increasing the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown below mirroring the bestfits file. The first column is the log-likelihood, then the corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| log-likelihood | nu1 | nu2  | T    | m    | misid | theta |
|----------------|-----|------|------|------|-------|-------|
| -1358.66       | 2.2 | 0.52 | 0.29 | 1.24 | 0.021 | 6772  |
