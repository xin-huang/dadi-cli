# dadi-cli

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE)
[![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)
[![build Status](https://app.travis-ci.com/xin-huang/dadi-cli.svg?branch=master)](https://app.travis-ci.com/github/xin-huang/dadi-cli)
[![codecov](https://codecov.io/gh/xin-huang/dadi-cli/branch/master/graph/badge.svg?token=GI66f4R3RF)](https://codecov.io/gh/xin-huang/dadi-cli)

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data based on diffusion approximation. However, using `dadi` requires knowledge of python and patience to tune different models.

## Installation

To install `dadi-cli`, users can use `pip`.

    pip install -i https://test.pypi.org/simple/ dadi-cli==0.8.1

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

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 50 50 --polarized --output ./examples/results/1KG.YRI.CEU.100.synonymous.snps.unfold.fs
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 50 50 --polarized --output ./examples/results/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

    NA12718	CEU
    NA12748	CEU
    NA12775	CEU
    NA19095	YRI
    NA19096	YRI
    NA19107	YRI

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haploidtypes for YRI and CEU respectively. We use a lower projection here, because it allows us to speed up examples.

By default, `dadi-cli` generates folded spectrum. To generate unfold spectrum, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

### Inferring demographic models

For inferring demographic models, we use the spectrum from the synonymous SNPs. Here, we use the `split_mig` model. In this model, the ancestral population diverges into two populations, which then have an instantaneous change of population size with migration between the two populations overtime. To find out the parameters of the `split_mig` model, users can use `dadi-cli Model --names split_mig`.

To start the inference, users should choose the initial value for each of the parameters with `--p0`, and specify the lower bounds and upper bounds for these parameters with `--lbounds` and `--ubounds`. Beside the four parameters in the `split_mig` model, we also use `--misid` to include a parameter measuring the proportion of alleles that their ancestral states are misidentified as the last parameter. Therefore, we have five parameters in total. Because we need to run optimization several times to find out a converged result with maximum likelihood, users can use `--optimizations` to specify how many times the optimization will run, which is done parallel. As well, because our 1000 Genomes data is fairly large we can increase the maximum number of parameter sets each optimization will use with `--maxeval` and use our own grid points with `--grids`.

    dadi-cli InferDM --fs ./examples/results/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --constants 1 1 .5 1 .5 --grids 100 120 140 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params --optimizations 5 --maxeval 200

After the optimization, a file `./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.opt1` will be made. Users can use `BestFit` to obtain the best fit parameters.

    dadi-cli BestFit --input-prefix ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM --model split_mig --misid
    
The result is in a file `./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits`, which contains the convergent results and Top 100 results (though the previous example will have 50)
The results look like:

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDM --fs ./examples/results/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds -1 -1 -1 -1 -1 --lbounds -1 -1 -1 -1 -1 --grids 100 120 140 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params --optimizations 50 --maxeval 200
    #
    # Converged results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -5256.497420750247	2.228860256926072	0.6108203633107568	0.24035688267684766	0.8155149040521631	0.018598653624160102	6926.31574610221
    -5256.506391799175	2.2355713111956685	0.6108283239069959	0.23930712815692726	0.8107431852959477	0.018542627868296295	6927.002935227271
    -5256.510561170369	2.2338687866248623	0.6127856032197797	0.24005386203375031	0.8082129227728075	0.01866136360717148	6920.850180803427
    -5256.529194448397	2.223884874814425	0.6107343981588284	0.24017702570696048	0.8161272212077513	0.01859352572219784	6930.906872393411
    -5256.532099333823	2.240128098557569	0.6125020509433051	0.24102154981508941	0.8132672334568465	0.018631838218648052	6912.075385173006
    #
    # Top 100 results
    # Log(likelihood)	nu1	nu2	T	m	misid	theta
    -5256.497420750247	2.228860256926072	0.6108203633107568	0.24035688267684766	0.8155149040521631	0.018598653624160102	6926.31574610221
    -5256.506391799175	2.2355713111956685	0.6108283239069959	0.23930712815692726	0.8107431852959477	0.018542627868296295	6927.002935227271
    [...]
    -6851.557642668979	1.4784651666827264	0.3932958549613372	0.9068191217716736	2.230490842800757	0.019478100388863117	7244.17344812743
    
Because there is randomness built into dadi-cli for where the starting parameters are for each optimization, it is possible the results could have not converged. Some things that can be done when using `InferDM` are increasing the max number of parameter sets each optimization will attempt with the `--maxeval` option. Users can increase the number of optimizations with `--optimizations`.

Using `BestFit`, users can adjust the criteria for convergence. By default optimizations are considered convergent if there are two other optimizations with a log-likelihood within 0.05 units of the optimization with the best log-likelihood. This criteria can be adjusted using the `--delta-ll` option. Generally a higher `--delta-ll` can result in a false positive convergence, but this is dependent on the data being used. Optimizations in the bestfit file should be examined closely for similar parameters in convergent fits.

Finally, if you have experience with the data you are using, you can use the `--check-convergence` option in `InferDM`. This option will run `BestFit` after each optimization to check fo convergence and stop running optimizations once convergence is reached. When using `--check-convergence` you can pass in a `--delta-ll` as well to change the convergence criteria.

    dadi-cli InferDM --fs ./examples/results/1KG.YRI.CEU.100.synonymous.snps.unfold.fs --model split_mig --misid --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 100 120 140 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params --optimizations 300 --maxeval 200 --check-convergence --delta-ll 0.01

As the result suggests, our optimization is converged, and the best fit parameters are in `./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits`. However, some parameters may be close to the boundaries. Users should be cautious and may increase the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown in below. The first column is the likelihood corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| likelihood | nu1 | nu2 | T | m | misid | theta |
| - | - | - | - | - | - | - |
| -5256.5 | 2.23 | 0.61 | 0.24 | 0.81 | 0.019 | 6926.32 |

### Generating caches for DFE inference

After inferring the best fit demographic model, users may also infer DFE from data. To perform DFE inference, users need to generate caches at first. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel_single_gamma` model or the `split_mig_sel` model. The `split_mig_sel` model is used for inferring DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations. The `split_mig_sel_single_gamma` model can also be used for inferring DFE from a single population.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. `--mp` indicates using multiprocess to accelerate the computation. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are different in the two populations. If you want to to make the cache for the situation where the selection coefficients is the same in the two populations, use the `--single-gamma` option.

    dadi-cli GenerateCache --model split_mig --single-gamma --demo-popt ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --misid --sample-size 100 100 --grids 120 140 160 --output ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --mp
    
    dadi-cli GenerateCache --model split_mig --demo-popt ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --misid --sample-size 100 100 --grids 120 140 160 --output ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.spectra.bpkl --mp

### Inferring DFE

For inferring DFE, we use the spectrum from the nonsynonymous SNPs and an example from inferring joint DFE<sup>2</sup>. In joint DFE inference, we need two caches. `--cache1d` accepts the cache that assumes the population-scaled selection coefficients are the same in the two populations. `--cache2d` accepts the cache that assumes the population-scaled selection coefficients are different in the two populations. Here, we define the marginal DFE is a lognormal distribution with `--pdf1d` and the joint DFE is a bivariate lognormal distribution with `--pdf2d`. In total, we have five parameters: the mean of the lognormal distribution, the standard deviation of the lognormal distribution, the correlation coefficient of the bivariate lognormal distribution, one minus the DFE correlation coefficienct, and the misidentification for the ancestral states. We fix the correlation coefficient in the bivariate lognormal distribution (the third parameter) to be zero with `--constants`. `-1` indicates there is no boundary or not fixed for a parameter. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. Here is an example of running with `--pdf1d lognormal`, which just uses `mu`, `sigma`, and `misid` for parameters.

    dadi-cli InferDFE --fs ./examples/results/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --misid --pdf1d lognormal --p0 1 1 .5 --lbounds 0 0.01 0 --ubounds 10 10 1 --demo-popt ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/optimization1/1KG.YRI.CEU.100.split_mig.dfe.params --optimizations 100 --maxeval 500

After the optimization, users can use `BestFit` to obtain the best fit parameters and save it in `./examples/results/dfe/optimization1/1KG.YRI.CEU.100.split_mig.dfe.params.InferDFE.bestfit`.

    dadi-cli BestFit --input-prefix ./examples/results/dfe/optimization1/1KG.YRI.CEU.100.split_mig.dfe.params.InferDFE --pdf lognormal --model split_mig --misid
    
The result is

    # /home/u25/tjstruck/anaconda3/envs/dadicli/bin/dadi-cli InferDFE --fs ./examples/results/1KG.YRI.CEU.100.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.100.split_mig.sel.single.gamma.spectra.bpkl --misid --pdf1d lognormal --p0 1 1 .5 --lbounds 0 0.01 0 --ubounds 10 10 1 --demo-popt ./examples/results/demo/optimization1/1KG.YRI.CEU.100.split_mig.demo.params.InferDM.bestfits --ratio 2.31 --output ./examples/results/dfe/optimization1/1KG.YRI.CEU.100.split_mig.dfe.params --optimizations 100 --maxeval 500
    #
    # Converged results
    # Log(likelihood)	log(mu)	log(sigma)	misid	theta
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    #
    # Top 100 results
    # Log(likelihood)	log(mu)	log(sigma)	misid	theta
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    -15043.4631087791	0.44761577504254146	1.186665070205059	0.012629375151270475	15926.683036368815
    [...]
    -15309.798890938577	0.6485327848469901	1.1493883082058935	0.01651677445440453	15926.683036368815

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`, the first column is the likelihood.

| likelihood | mu | sigma | misidentification |
| - | - | - | - | - | - |
| -27880.309 | 0.447  | 1.186  | 0.0126 |

### Performing statistical testing

To performing statistical testing with the Godambe Information Matrix, users should first use `GenerateFs` to generate bootstrapping data from VCF files.

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.100.synonymous.snps.unfold
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 100 100 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.100.nonsynonymous.snps.unfold
    
To estimate the confidence intervals for the demographic parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.synonymous.snps.unfold.fs --demo-model IM_pre --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --bootstrapping-dir ./examples/results/fs/bootstrapping_syn/ --output ./examples/results/stat/1KG.YRI.CEU.IM_pre.bestfit.demo.params.godambe.ci
    
To estimate the confidence intervals for the joint DFE parameters, users can use

    dadi-cli Stat --fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.IM_pre.bestfit.dfe.params --bootstrapping-dir ./examples/results/fs/bootstrapping_non/ --ratio 2.31 --output ./examples/results/stat/1KG.YRI.CEU.IM_pre.bestfit.dfe.params.godambe.ci

### Plotting

`dadi-cli` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.synonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.synonymous.snps.unfold.fs.pdf
    
    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs.pdf
    
To compare two frequency spectra from data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.synonymous.snps.unfold.fs --fs2 ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --output ./examples/results/plots/1KG.YRI.CEU.synonymous.vs.nonsynonymous.snps.unfold.fs.pdf
    
To compare frequency spectra between a demographic model without selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.synonymous.snps.unfold.fs --demo-model IM_pre --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --output ./examples/results/plots/1KG.YRI.CEU.synonymous.snps.vs.IM_pre.pdf
    
To compare frequency spectra between a demographic model with selection and data, users can use

    dadi-cli Plot --fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --ratio 2.31 --dfe-popt ./examples/results/dfe/1KG.YRI.CEU.IM_pre.bestfit.dfe.params --cache1d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --pdf1d lognormal --pdf2d biv_lognormal --output ./examples/results/plots/1KG.YRI.CEU.nonsynonymous.snps.vs.joint.lognormal.mixture.pdf
    
By default, `dadi-cli` projects the sample size down to 20 for each population. Users can use `--projections` to change the sample size.
    
### Available demographic models

`dadi-cli` provides a subcommand `Model` to help users finding available demographic models in `dadi`.
To find out available demographic models, users can use

    dadi-cli Model --names
    
Then the available demographic models will be displayed in the screen:

    Available 1D demographic models:
    - bottlegrowth_1d
    - growth_1d
    - snm_1d
    - three_epoch_1d
    - two_epoch_1d

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
    - mixture

To find out the parameters and detail of a specific model, users can use the name of the demograpic model as the parameter after `--names`. For example,

    dadi-cli Model --names IM
    
Then the detail of the model will be displayed in the screen:

    - IM_pre:

        Isolation-with-migration model with exponential pop growth and a size change
        prior to split.
        Two populations in this model.

        params = [nuPre,TPre,s,nu1,nu2,T,m12,m21]

            nuPre: Size after first size change (in units of Na)
             TPre: Time before split of first size change (in units of 2*Na generations)
                s: Fraction of nuPre that goes to pop1 (Pop 2 has size nuPre*(1-s))
              nu1: Final size of pop 1 (in units of Na)
              nu2: Final size of pop 2 (in units of Na)
                T: Time in the past of split (in units of 2*Na generations)
              m12: Migration from pop 2 to pop 1 (2*Na*m12)
              m21: Migration from pop 1 to pop 2 (2*Na*m21)

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

To find out the parameters and the detail of a specific function, users can use the name of the function as the parameter after `--names`. For example,

    dadi-cli Pdf --names beta
    
Then the detail of the function will be displayed in the screen:

    - beta:

            Beta probability density function.

            params = [alpha, beta]

## Dependencies

- [dadi 2.1.0](https://bitbucket.org/gutenkunstlab/dadi/src/master/)

## References

1. [Gutenkunst et al., *PLoS Genet*, 2009.](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000695)
2. [Huang et al., *Mol Biol Evol*, 2021.](https://doi.org/10.1093/molbev/msab162)
