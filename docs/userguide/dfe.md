# DFE inference

## Input

After obtaining the cache file [1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl), we can fit the spectrum from nonsynonymous SNPs for DFE inference. Although our data come from two populations, we will first infer a one-dimensional DFE, which assumes that selection coefficients are equal in the two populations. An example command is below:

```
dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache1d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence 5 --cpus 2
```

Many arguments are the same as those in the `InferDM` command.

Furthermore, we can define the marginal DFE as a lognormal distribution with `--pdf1d`, and use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs.

To see descriptions of the parameters in the `lognormal` distribution, users can use:

```
dadi-cli Pdf --names lognormal
```

which returns:

```
- lognormal:

            Lognormal probability density function.

            params = [log_mu, log_sigma]
```

Here, `log_mu` is the mean of the lognormal distribution, and `log_sigma` is the standard deviation of the lognormal distribution.

## Output

The results stored in [1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params.InferDFE.bestfits) are:

```
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache1d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence 5 --cpus 2
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache1d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel_single_gamma.spectra.bpkl --pdf1d lognormal --p0 1 1 .5 --lbounds -10 0.01 0 --ubounds 10 10 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.1D_lognormal.params --optimizations 10 --maxeval 400 --check-convergence 5 --cpus 2
#
# Converged results
# Log(likelihood)	log_mu	log_sigma	misid	theta
-1390.216558502869	5.7078081159785725	7.934694578672994	0.01647346102391192	15691.446711371886
-1390.2206755646514	5.696866719099689	7.910257538672334	0.016549081772691945	15691.446711371886
-1390.2321802957717	5.6985080744503795	7.915039953288335	0.01632034569197264	15691.446711371886
#
# Top 100 results
# Log(likelihood)	log_mu	log_sigma	misid	theta
-1390.216558502869	5.7078081159785725	7.934694578672994	0.01647346102391192	15691.446711371886
-1390.2206755646514	5.696866719099689	7.910257538672334	0.016549081772691945	15691.446711371886
-1390.2321802957717	5.6985080744503795	7.915039953288335	0.01632034569197264	15691.446711371886
-1390.5785860284573	5.838670032124382	8.202117596248334	0.016267679223638656	15691.446711371886
-1391.602004080164	5.883742893394162	8.301911448575662	0.015025267493752754	15691.446711371886
-2851.693923307018	0.9456483751405087	0.2546946309528162	0.03942740949097054	15691.446711371886         
```

which is similar to the file [1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits) from the `InferDM` command.

## Joint DFE inference

Besides inferring one-dimensional DFEs, we can also analyze the joint DFE or quantify the correlation between DFEs in two populations. This is done using the joint allele frequency spectrum, under the assumption that the selection coefficients are independent in each population<sup>2</sup>.

### Inferring a bivariate lognormal joint DFE

Here, we can infer a joint DFE with selection potentially being different in the two populations using the following command:

```
dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache2d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.biv_lognormal.params --force-convergence 10 --cpus 128
```

We define the DFE as a bivariate lognormal distribution with `--pdf2d` and pass in a cache (e.g., [1KG.YRI.CEU.20.split_mig_sel.spectra.bpkl](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/caches/1KG.YRI.CEU.20.split_mig_sel.spectra.bpkl)) that assumes the population-scaled selection coefficients are different in the two populations through `--cache2d`. 


The best-fit results from the above command are stored in [1KG.YRI.CEU.20.split_mig.dfe.biv_lognormal.params.InferDFE.bestfits](https://github.com/xin-huang/dadi-cli/blob/revision/examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.biv_lognormal.params.InferDFE.bestfits) and look like:

```
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache2d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.biv_lognormal.params --force-convergence 10 --cpus 128
# /Users/user/mambaforge/envs/dadi-cli-cpu/bin/dadi-cli InferDFE --fs examples/results/fs/1KG.YRI.CEU.20.non.unfolded.fs --cache2d examples/results/caches/1KG.YRI.CEU.20.split_mig_sel.spectra.bpkl --pdf2d biv_lognormal --p0 1 1 1 1 .5 .5 --lbounds -10 -10 0.01 0.01 0.001 0 --ubounds 10 10 10 10 0.999 0.5 --demo-popt examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output-prefix examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.biv_lognormal.params --force-convergence 10 --cpus 128
#
# Converged results
# Log(likelihood)	log_mu1	log_sigma1	log_mu2	log_sigma2	rho	misid	theta
-1269.7688158561698	3.496765165218968	3.713425228640547	3.3489414810581377	2.6233786532528143	0.9988080368472209	0.013328659186589912	15691.446711371886
-1269.792126279663	3.128291713144148	3.421135576024593	3.186303154478381	2.514221425732018	0.9988076145452933	0.013702129045609968	15691.446711371886
-1269.8877978967253	3.0240471911322313	3.3454245244505976	3.0473363107678586	2.3992755341484835	0.9986348102628311	0.014090425518404406	15691.446711371886
#
# Top 100 results
# Log(likelihood)	log_mu1	log_sigma1	log_mu2	log_sigma2	rho	misid	theta
-1269.7688158561698	3.496765165218968	3.713425228640547	3.3489414810581377	2.6233786532528143	0.9988080368472209	0.013328659186589912	15691.446711371886
-1269.792126279663	3.128291713144148	3.421135576024593	3.186303154478381	2.514221425732018	0.9988076145452933	0.013702129045609968	15691.446711371886
-1269.8877978967253	3.0240471911322313	3.3454245244505976	3.0473363107678586	2.3992755341484835	0.9986348102628311	0.014090425518404406	15691.446711371886
-1269.9768426449568	3.402552377296842	3.6352537861478456	3.293520359555489	2.5218120840365947	0.999	0.013553877933897708	15691.446711371886
-1270.1749230540172	3.004289099264522	3.31239816183356	3.3706123914881956	2.677877497950098	0.9989894576849508	0.012896735682239547	15691.446711371886
-1270.2393868987194	3.4127788846571487	3.6436099931488393	3.349659056851049	2.560962685456004	0.999	0.013358245693701804	15691.446711371886
-1270.255094793673	3.5271192261011777	3.7268942107340144	3.740359538817612	2.966809407053775	0.999	0.013398534572324667	15691.446711371886
-1270.4034392718133	3.1272513385462704	3.4156165650909025	3.321722351328588	2.6311679352352364	0.998887151654479	0.014509122413232493	15691.446711371886
-1270.4486445522762	3.0464337787417115	3.3711318845681606	2.9341408629023156	2.2816973032386105	0.9985513367584204	0.014223720395626535	15691.446711371886
-1270.6884149515372	1.708994689384669	2.2742510209018523	2.5459076510477185	2.0317673702672434	0.9983759848347304	0.013288635793938096	15691.446711371886
```

The bivariate lognormal distribution has an extra parameter `rho`, which represents the correlation of the DFE between the populations. We can allow `log_mu` and `log_sigma` to be either the same or different in our populations. `dadi-cli` will run either the symmetric (shared `log_mu` and `log_sigma`) or asymmetric (independent `log_mu` and `log_sigma`) bivariate lognormal distribution based on the number of parameters: three parameters for the symmetric distribution and five parameters for the asymmetric distribution.

For the symmetric bivariate lognormal distribution, the parameters are `log_mu`, `log_sigma`, and `rho`. For the asymmetric bivariate lognormal distribution, the parameters are `log_mu1`, `log_mu2`, `log_sigma1`, `log_sigma2`, and `rho`, where `1` denotes the first population and `2` denotes the second population.

### Inferring mixture model joint DFE

Here, we will use a mixture of a univariate lognormal and a bivariate lognormal distribution. To make the mixture we pass in options for both 1D and 2D: `--pdf1d`, `--pdf2d`, `--cache1d`, and `--cache2d`. Because the mixture model is assuming some proportion of the DFE is lognormal and the other is bivariate, the bivariate is symmeteric. The parameters for the mixture lognormal DFE are `log_mu`, `log_sigma`, `rho`,and `w`, the proportional weight of the bivariate lognormal DFE (1-`w` would be the weight of the univariate lognormal distribution). In this example we fix `rho` of the bivariate component to 0 with the `--constants` option.

```
dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --mix-pdf mixture_lognormal --p0 1 1 0 .5 .5 --lbounds -10 0.01 -1 0.001 0 --ubounds 10 10 -1 0.999 0.5 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 15 --maxeval 400 --check-convergence 10
```

Similar to the best fit parameters in `./examples/results/demog/1KG.YRI.CEU.split_mig.bestfit.demog.params`, the first column is the log-likelihood.

| likelihood | mu   | sigma | rho | w   | misidentification |
|------------|------|-------|-----|-----|-------------------|
| -1389      | 5.51 | 7.65  | 0   | 0   | 0.017             |

## Arguments

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
| `--constants`           | Fixed parameters during the inference or using Godambe analysis. Use -1 to indicate a parameter is NOT fixed. Default: None. |
| `--lbounds`             | Lower bounds of the optimized parameters. |
| `--ubounds`             | Upper bounds of the optimized parameters. |
| `--global-optimization` | Use global optimization before doing local optimization. Default: False. |
| `--seed`                | Random seed. |
