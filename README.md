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

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --output ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --output ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs

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

To start the inference, users should choose the initial value for each of the parameters with `--p0`, and specify the lower bounds and upper bounds for these parameters with `--lbounds` and `--ubounds`. We can fix parameters with `--constants`. `-1` indicates there is no boundary or not fixed for a parameter. Beside the four parameters in the `split_mig` model, we also use `--misid` to include a parameter measuring the proportion of alleles that their ancestral states are misidentified as the last parameter. Therefore, we have five parameters in total. Because we need to run optimization several times to find out a converged result with maximum likelihood, users can use `--optimizations` to specify how many times the optimization will run. The `--threads` option will allow you to pass in the number of CPUs you want to use to run optimizations in parallele. As well, because our 1000 Genomes data is fairly large we can increase the maximum number of parameter sets each optimization will use with `--maxeval` and use our own grid points with `--grids`.

    dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 100 120 140 --output ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params --optimizations 5 --threads 5 --maxeval 200

After the optimization, a file `./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.opts.0` will be made. Users can use `BestFit` to obtain the best fit parameters.

    dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM --model split_mig --misid
    
The result is in a file `./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits`, which contains the convergent results and Top 100 results (though this example will have 5 results due to the number of optimizations ran)
The results look like:

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli BestFit --input-prefix ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM --model split_mig --misid
    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 100 120 140 --output ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params --optimizations 5 --threads 5 --maxeval 200
    #
    # Converged results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -12784.139486984966	2.2644587230068765	0.7372641175414204	0.23547579502498336	0.5818246179625153	0.017096108308743536	6908.904382567545
    -12784.437516148671	2.2804742661171424	0.7402142199978113	0.23780437049969316	0.5871777028364891	0.017193058360337524	6878.545507866014
    -12785.28070682328	2.276506945514596	0.7378874120550815	0.24029223372605218	0.6004532020200654	0.017177430162106804	6872.991205656402
    #
    # Top 100 results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -12784.139486984966	2.2644587230068765	0.7372641175414204	0.23547579502498336	0.5818246179625153	0.017096108308743536	6908.904382567545
    -12784.437516148671	2.2804742661171424	0.7402142199978113	0.23780437049969316	0.5871777028364891	0.017193058360337524	6878.545507866014
    -12785.28070682328	2.276506945514596	0.7378874120550815	0.24029223372605218	0.6004532020200654	0.017177430162106804	6872.991205656402
    -12785.838279522275	2.2586283110345113	0.7306934423044463	0.2385939362647791	0.6090328825227941	0.017034362289712012	6908.739065406204
    -24634.506178417512	3.7022046379763784	0.7620191186942221	0.8827889268055473	1.1683407621823954	0.22296204228059485	4513.334779174665
    
Because there is randomness built into dadi-cli for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can also try to use a global optimization before moving onto the local optimization with the `--global-optimization` option. Do know that the number of optimizations specified will be the same for both the global and local optimization.

Using `BestFit`, users can adjust the criteria for convergence. By default optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.01% units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option and passing in the percentage difference in decimal form (so the default is 0.0001, rather than 0.01). Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used (especially the sample size can effect the size of the log-likelihood). Optimizations in the bestfit file will be ordered by log-likelihood and should be examined closely for similarity of parameter values in convergent fits.

Finally, if you have experience with the data you are using, you can use the `--check-convergence` or `--force-convergence` option in `InferDM`. The `--check-convergence` option will run `BestFit` after each optimization to check for convergence and stop running optimizations once convergence is reached. The `--force-convergence` option will constantly add new optimization runs until convergence is reached. When using `--check-convergence` or `--force-convergence` you can pass in a value with `--delta-ll` as well to change the convergence criteria.

Sometimes parameters may be close to the boundaries. Users should be cautious and test increasing the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown below mirroring the bestfits file. The first column is the log-likelihood, then the corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| log-likelihood | nu1 | nu2 | T | m | misid | theta |
| - | - | - | - | - | - | - |
| -12784.14 | 2.26 | 0.74 | 0.24 | 0.58 | 0.017 | 6908.9 |

### Generating caches for DFE inference

After inferring the best fit demographic model, users may also infer DFE from data. To perform DFE inference, users need to generate caches at first. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel` model or the `split_mig_sel_single_gamma` model. The `split_mig_sel` model is used for inferring the DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. `--mp` indicates using multiprocess to accelerate the computation. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are different in the two populations. If you want to to make the cache for the situation where the selection coefficients is the same in the two populations, use the `--single-gamma` option. You can use the `--gamma-bounds` option to choose the range of the gamma distribution and the `--gamma-pts` option can be used to specify the number of selection coefficients that will be selected in that range to generate your cache.

    dadi-cli GenerateCache --model split_mig --single-gamma --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --misid --sample-size 100 100 --grids 120 140 160 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --mp

    dadi-cli GenerateCache --model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --misid --sample-size 100 100 --grids 120 140 160 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.spectra.bpkl --mp

### Inferring DFE

For inferring the DFE, we use the spectrum from the nonsynonymous SNPs and an example from inferring joint DFE<sup>2</sup>. In joint DFE inference, we can use a 1D and/or 2D caches depending on the DFE we want to use. `--cache1d` accepts the cache that assumes the population-scaled selection coefficients are the same in the two populations. `--cache2d` accepts the cache that assumes the population-scaled selection coefficients are different in the two populations. Here, we will use a mixture of lognormal distributions. We define the marginal DFE as a lognormal distribution with `--pdf1d` and we define the joint DFE as a bivariate lognormal distribution with `--pdf2d`. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. Here is an example of running with `--pdf1d lognormal` and `--pdf2d biv_lognormal` with the `--misid` option, so our parameters are `log_mu` the mean of the lognormal distribution, `log_sigma` the standard deviation of the lognormal distribution, `rho` the correlation coefficient for the bivariate lognormal, and `w` the weight of the bivariate distribution (1-w is the weight of the lognormal distribution), and `misid` the misidentification for the ancestral states. Here we fix `rho` to 0 with the `--constants` option.

    dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.spectra.bpkl --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.100.split_mig.dfe.lognormal_mixture.params --optimizations 5 --threads 5 --maxeval 400 --check-convergence

The result is

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDFE --fs ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.spectra.bpkl --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds 0 0.01 -1 0 0 --ubounds 10 10 -1 0 1 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/1KG.YRI.CEU.100.split_mig.dfe.lognormal_mixture.params --optimizations 20 --threads 10 --maxeval 400 --force-convergence
    #
    # Converged results
    # Log(likelihood)	log_mu	log_sigma	rho	w	misid	theta
    -13256.61108936973	2.2305168477940738	4.2743477044322296	0.0	0.0	0.011616109073834592	16037.834951340008
    -13256.61758577463	2.230439697200394	4.273469888150792	0.0	0.0	0.011614738184195932	16037.834951340008
    -13256.625614584696	2.230412957619967	4.273782157759427	0.0	0.0	0.011616615627266364	16037.834951340008
    #
    # Top 100 results
    # Log(likelihood)	log_mu	log_sigma	rho	w	misid	theta
    -13256.61108936973	2.2305168477940738	4.2743477044322296	0.0	0.0	0.011616109073834592	16037.834951340008
    -13256.61758577463	2.230439697200394	4.273469888150792	0.0	0.0	0.011614738184195932	16037.834951340008
    -13256.625614584696	2.230412957619967	4.273782157759427	0.0	0.0	0.011616615627266364	16037.834951340008

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.split_mig.bestfit.demo.params`, the first column is the likelihood.

| likelihood | mu | sigma | rho | w | misidentification |
| - | - | - | - |
| -13256.61108936973 | 2.2305168477940738  | 4.2743477044322296 | 0 | 0 | 0.0116 |

### Performing statistical testing

To performing statistical testing with the Godambe Information Matrix, users should first use `GenerateFs` to generate bootstrapping data from VCF files.

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.100.synonymous.snps.unfold

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.100.nonsynonymous.snps.unfold

To estimate the confidence intervals for the demographic parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --grids 120 140 160 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.100.split_mig.bestfit.demo.params.godambe.ci

To estimate the confidence intervals for the joint DFE parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --model split_mig --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.100.split_mig.dfe.lognormal.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --grids 120 140 160 --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_non/ --output ./examples/results/stat/1KG.YRI.CEU.100.split_mig.bestfit.dfe.lognormal.params.godambe.ci


### Plotting

`dadi-cli` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.100.synonymous.snps.unfold.fs.pdf --model split_mig
    
    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs.pdf --model split_mig
    
To compare two frequency spectra from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --fs2 ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.100.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf --model None
    
To compare frequency spectra between a demographic model without selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --demo-popt ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --misid --output ./examples/results/plots/1KG.YRI.CEU.100.synonymous.snps.vs.split_mig.pdf --model split_mig
    
To compare frequency spectra between a demographic model with selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --misid --model split_mig --pdf1d lognormal --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.100.split_mig.dfe.lognormal.params.InferDFE.bestfits --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --output ./examples/results/plots/1KG.YRI.CEU.100.nonsynonymous.snps.vs.lognormal.pdf
    
By default, `dadi-cli` projects the sample size down to 20 for each population. Users can use `--projections` to change the sample size.

### Using WorkQueue for distributed inference with dadi-cli

`dadi-cli` `InferDM` and `InferDFE` has built in options to work with  Cooperative Computing Tools (`CCTools`)'s `Work Queue` for launching independent optimizations across multiple machines. This example will be for submitting jobs to a `Slurm Workload Manager`. First we want to submit a factory.

    work_queue_factory -T slurm -M dm-inference -P mypwfile --workers-per-cycle=0 --cores=1 &
    
`dm-inference` is the project name and `mypwfile` is a file containing a password, both of which are needed for `dadi-cli` use. Next you'll want to submit jobs from `dadi-cli`.

    dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 100 120 140 --output ./examples/results/demo/1KG.YRI.CEU.100.split_mig.demo.check-convergence.params --optimizations 90 --maxeval 400 --work-queue dm-inference mypwfile

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
