# dadi-cli

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE)
[![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)
[![build Status](https://app.travis-ci.com/xin-huang/dadi-cli.svg?branch=master)](https://app.travis-ci.com/github/xin-huang/dadi-cli)
[![codecov](https://codecov.io/gh/xin-huang/dadi-cli/branch/master/graph/badge.svg?token=GI66f4R3RF)](https://codecov.io/gh/xin-huang/dadi-cli)

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data based on diffusion approximation. However, using `dadi` requires knowledge of python and patience to tune different models.

## Installation

To install `dadi-cli`, users should clone this repo and use the following command

    python setup.py install

To get help information, users can use

    dadi-cli -h

There are nine subcommands in `dadi-cli`: 
- `GenerateFs`
- `GenerateCache`
- `InferDM`
- `InferDFE`
- `BestFit` 
- `Stat`
- `Plot`
- `Model`
- `Pdf`

To display help information for each subcommand, users can use

    dadi-cli subcommand -h
    
For example,

    dadi-cli GenerateFs -h

## The workflow

## Usage: An Example

Here we use the data from the 1000 Genomes Project to demonstrate how to apply `dadi-cli` in research.

### Generating allele frequency spectrum from VCF files

`dadi-cli` only accepts VCF files to generate allele frequency spectrum. To generate the spectrum, users can use

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --output ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

    NA12718	CEU
    NA12748	CEU
    NA12775	CEU
    NA19095	YRI
    NA19096	YRI
    NA19107	YRI

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haploidtypes for YRI and CEU respectively. We use a lower sample size here, because it allows us to speed up examples.

By default, `dadi-cli` generates folded spectrum. To generate unfold spectrum, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

### Inferring demographic models

For inferring demographic models, we use the spectrum from the synonymous SNPs. Here, we use the `split_mig` model. In this model, the ancestral population diverges into two populations, which then have an instantaneous change of population size with migration between the two populations overtime. To find out the parameters of the `split_mig` model, users can use `dadi-cli Model --names split_mig`.

To start the inference, users should choose the initial value for each of the parameters with `--p0`, and specify the lower bounds and upper bounds for these parameters with `--lbounds` and `--ubounds`. For demographic models, setting parameter boundaries helps prevent optimizers from going into parameter spaces that are hard for dadi to calculate, such as low population size, high time, and high migration. We can fix parameters with `--constants`. `-1` indicates there is no boundary or not fixed for a parameter. Beside the four parameters in the `split_mig` model, we also use `--misid` to include a parameter measuring the proportion of alleles that their ancestral states are misidentified as the last parameter. Therefore, we have five parameters in total. Because we need to run optimization several times to find out a converged result with maximum likelihood, users can use `--optimizations` to specify how many times the optimization will run. `dadi-cli` can use multiprocessing to run optimizations in parallel and by default the max number of CPUs available will be utilized. If users want fewer CPUs to be used, they can use the `--threads` option to pass in the number of CPUs they want utilized for multiprocessing. As well, because our 1000 Genomes data is fairly large we can increase the maximum number of parameter sets each optimization will use with `--maxeval` and use our own grid points with `--grids`.

    dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 10 --maxeval 200

After the optimization, a file `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.opts.0` will be made. Users can use `BestFit` to obtain the best fit parameters.

    dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM --model split_mig --misid
    
The result is in a file `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits`, which contains the convergent results and Top 100 results (though this example will have fewer results due to the number of optimizations ran)
The results look like:

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM --model split_mig --misid
    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 5 --maxeval 200 --force-convergence
    #
    # Converged results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -1358.6558310915505	2.20027395455651	0.5152831850400569	0.2849676037903571	1.2387949067465094	0.020600295100081403	6772.40314409887
    -1358.659947037239	2.2005989448681142	0.5148963770196837	0.2840803044097646	1.235637293625369	0.02065318030399088	6776.507232358916
    -1358.6619126545752	2.193467416083568	0.5150274155590934	0.28576672266378395	1.242327405753632	0.020736506112440684	6773.040318241413
    [...]
    -1358.7245745624227	2.200809125602347	0.5169518650066209	0.28428157652364877	1.226847237753732	0.020675739947299824	6771.292051845249
    #
    # Top 100 results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -1358.6558310915505	2.20027395455651	0.5152831850400569	0.2849676037903571	1.2387949067465094	0.020600295100081403	6772.40314409887
    -1358.659947037239	2.2005989448681142	0.5148963770196837	0.2840803044097646	1.235637293625369	0.02065318030399088	6776.507232358916
    -1358.6619126545752	2.193467416083568	0.5150274155590934	0.28576672266378395	1.242327405753632	0.020736506112440684	6773.040318241413
    -1358.6684376919432	2.192449630031461	0.5153959559584439	0.2865384568706404	1.2424629664085745	0.020655634536391836	6769.637245461502
    -1358.6754932408107	2.1965485931130626	0.5163722970750675	0.28631981227934206	1.236433338533083	0.020683244587333297	6766.39298337399
    [...]
    -1433.8543354432443	1.9519216565759065	0.50915723496404	0.49626260162548375	1.5668249133277081	0.024358069148502002	6327.491539563679
    
Because there is randomness built into dadi-cli for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can also try to use a global optimization before moving onto the local optimization with the `--global-optimization` option. 25% of the number of optimizations the user passes in will be used for the global and the remaining will be used for the local optimization.

Using `BestFit`, users can adjust the criteria for convergence. By default optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.01% units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option and passing in the percentage difference in decimal form (so the default is 0.0001, rather than 0.01). Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used (especially the sample size can effect the size of the log-likelihood). Optimizations in the bestfit file will be ordered by log-likelihood and should be examined closely for similarity of parameter values in convergent fits.

Finally, if you have experience with the data you are using, you can use the `--check-convergence` or `--force-convergence` option in `InferDM`. The `--check-convergence` option will run `BestFit` after each optimization to check for convergence and stop running optimizations once convergence is reached. The `--force-convergence` option will constantly add new optimization runs until convergence is reached. When using `--check-convergence` or `--force-convergence` you can pass in a value with `--delta-ll` as well to change the convergence criteria.

Sometimes parameters may be close to the boundaries. Users should be cautious and test increasing the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown below mirroring the bestfits file. The first column is the log-likelihood, then the corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| log-likelihood | nu1 | nu2 | T | m | misid | theta |
| - | - | - | - | - | - | - |
| -1358.66 | 2.2 | 0.52 | 0.28 | 1.24 | 0.021 | 6772 |

### Generating caches for DFE inference

After inferring the best fit demographic model, users may also infer DFE from data. To perform DFE inference, users need to generate caches at first. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel` model or the `split_mig_sel_single_gamma` model. The `split_mig_sel` model is used for inferring the DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. `--mp` indicates using multiprocess to accelerate the computation. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are different in the two populations. If you want to to make the cache for the situation where the selection coefficients is the same in the two populations, use the `--single-gamma` option. You can use the `--gamma-bounds` option to choose the range of the gamma distribution and the `--gamma-pts` option can be used to specify the number of selection coefficients that will be selected in that range to generate your cache.

    dadi-cli GenerateCache --model split_mig --single-gamma --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --misid --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --mp

    dadi-cli GenerateCache --model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --misid --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --mp

### Inferring DFE

For inferring the DFE, we use the spectrum from the nonsynonymous SNPs and an example from inferring joint DFE<sup>2</sup>. In joint DFE inference, we can use a 1D and/or 2D caches depending on the DFE we want to use. `--cache1d` accepts the cache that assumes the population-scaled selection coefficients are the same in the two populations. `--cache2d` accepts the cache that assumes the population-scaled selection coefficients are different in the two populations. Here, we will use a mixture of lognormal distributions. We define the marginal DFE as a lognormal distribution with `--pdf1d` and we define the joint DFE as a bivariate lognormal distribution with `--pdf2d`. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. Here is an example of running with `--pdf1d lognormal` and `--pdf2d biv_lognormal` with the `--misid` option, so our parameters are `log_mu` the mean of the lognormal distribution, `log_sigma` the standard deviation of the lognormal distribution, `rho` the correlation coefficient for the bivariate lognormal, and `w` the weight of the bivariate distribution (1-w is the weight of the lognormal distribution), and `misid` the misidentification for the ancestral states. Here we fix `rho` to 0 with the `--constants` option.

    dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 5 --maxeval 400 --check-convergence

The result is

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params --optimizations 5 --maxeval 400 --check-convergence
    #
    # Converged results
    # Log(likelihood)	log_mu	log_sigma	rho	w	misid	theta
    -1388.9783697999487	5.508927732043908	7.654086541996892	0.0	0.0	0.01654293421125699	15644.25126286839
    -1388.9785536049772	5.509044464904789	7.652783862354717	0.0	0.0	0.016563830198126888	15644.25126286839
    -1388.978715739256	5.507014007582351	7.649376164773611	0.0	0.0	0.01652802148251414	15644.25126286839
    #
    # Top 100 results
    # Log(likelihood)	log_mu	log_sigma	rho	w	misid	theta
    -1388.9783697999487	5.508927732043908	7.654086541996892	0.0	0.0	0.01654293421125699	15644.25126286839
    -1388.9785536049772	5.509044464904789	7.652783862354717	0.0	0.0	0.016563830198126888	15644.25126286839
    -1388.978715739256	5.507014007582351	7.649376164773611	0.0	0.0	0.01652802148251414	15644.25126286839
    -2807.955859125291	0.9151823457507116	0.23378097038602033	0.0	0.0	0.03923288724961618	15644.25126286839

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.split_mig.bestfit.demo.params`, the first column is the likelihood.

| likelihood | mu | sigma | rho | w | misidentification |
| - | - | - | - |
| -1389 | 5.51  | 7.65 | 0 | 0 | 0.017 |

### Performing statistical testing

To performing statistical testing with the Godambe Information Matrix, users should first use `GenerateFs` to generate bootstrapping data from VCF files. In this example we generate 20 bootstraps to save on time, but we recommend users do 100. `--chunk-size` is the max length of chunks the chromosomes will be broken up into and used to randomly draw from with replacement to make our bootstrapped chromosomes.

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.20.synonymous.snps.unfold

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 20 20 --polarized --bootstrap 20 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.20.nonsynonymous.snps.unfold

To estimate the confidence intervals for the demographic parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --grids 60 80 100 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.demo.params.godambe.ci

To estimate the confidence intervals for the joint DFE parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --model split_mig --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --grids 60 80 100 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_non/ --output ./examples/results/stat/1KG.YRI.CEU.20.split_mig.bestfit.dfe.lognormal_mixture.params.godambe.ci


### Plotting

`dadi-cli` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.unfold.fs.pdf --model split_mig

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs.pdf --model split_mig

To compare two frequency spectra from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --fs2 ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf --model None

To compare frequency spectra between a demographic model without selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --demo-popt ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params.InferDM.bestfits --misid --output ./examples/results/plots/1KG.YRI.CEU.20.synonymous.snps.vs.split_mig.pdf --model split_mig

To compare frequency spectra between a demographic model with selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.20.nonsynonymous.snps.unfold.fs --misid --model split_mig --pdf1d lognormal --pdf2d biv_lognormal --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.20.split_mig.dfe.lognormal_mixture.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --output ./examples/results/plots/1KG.YRI.CEU.20.nonsynonymous.snps.vs.lognormal_mixture.pdf
    
By default, `dadi-cli` projects the sample size down to 20 for each population. Users can use `--projections` to lower the sample size for visualization purposes.

### Using WorkQueue for distributed inference with dadi-cli

`dadi-cli` `InferDM` and `InferDFE` has built in options to work with  Cooperative Computing Tools (`CCTools`)'s `Work Queue` for launching independent optimizations across multiple machines. This example will be for submitting jobs to a `Slurm Workload Manager`. First we want to submit a factory.

    work_queue_factory -T slurm -M dm-inference -P mypwfile --workers-per-cycle=0 --cores=1 &
    
`dm-inference` is the project name and `mypwfile` is a file containing a password, both of which are needed for `dadi-cli` use. Next you'll want to submit jobs from `dadi-cli`.

    dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demo/1KG.YRI.CEU.20.split_mig.demo.params --optimizations 5 --maxeval 200 --check-convergence --work-queue dm-inference mypwfile

`dadi-cli` will send the number of workers as the number of optimizations you request. The `check-convergence` and `force-convergence` options work with `Work Queue` as well. 

### Available demographic models

`dadi-cli` provides a subcommand `Model` to help users finding available demographic models in `dadi`.
To find out available demographic models, users can use

    dadi-cli Model --names
    
Then the available demographic models will be displayed in the screen:

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

To find out the parameters and detail of a specific model, users can use the name of the demograpic model as the parameter after `--names`. For example,

    dadi-cli Model --names split_mig
    
Then the detail of the model will be displayed in the screen:

    - split_mig:
    
            Split into two populations of specifed size, with symmetric migration.
            Two populations in this model.
    
            params = [nu1,nu2,T,m]
        
                nu1: Size of population 1 after split (in units of Na)
                nu2: Size of population 2 after split (in units of Na)
                  T: Time in the past of split (in units of 2*Na generations) 
                  m: Migration rate between populations (2*Na*m)

### Available DFE distributions

`dadi-cli` provides a subcommand `Pdf` to help users finding available probability density functions for DFE inference in `dadi`.

To find out available probability density functions, users can use

    dadi-cli Pdf --names
    
Then the availalbe functions will be displayed in the screen:

    Available probability density functions:
    - beta
    - biv_ind_gamma
    - biv_lognormal
    - exponential
    - gamma
    - lognormal
    - normal
    - mixture

To find out the parameters and the detail of a specific function, users can use the name of the function as the parameter after `--names`. For example,

    dadi-cli Pdf --names lognormal
    
Then the detail of the function will be displayed in the screen:

    - lognormal:
    
            Lognormal probability density function.
    
            params = [log_mu, log_sigma]

## Dependencies

- [dadi 2.1.0](https://bitbucket.org/gutenkunstlab/dadi/src/master/)

## References

1. [Gutenkunst et al., *PLoS Genet*, 2009.](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000695)
2. [Huang et al., *Mol Biol Evol*, 2021.](https://doi.org/10.1093/molbev/msab162)
