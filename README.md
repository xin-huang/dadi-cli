# dadi-cli

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE)
[![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)

`dadi-cli` provides a command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data based on diffusion approximation. 

## Installation

To install `dadi-cli`, users can use `pip`.

    pip install -i https://test.pypi.org/simple/ dadi-cli==0.5.8

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

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --output ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --output ./examples/results/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

    NA12718	CEU
    NA12748	CEU
    NA12775	CEU
    NA19095	YRI
    NA19096	YRI
    NA19107	YRI

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haploidtypes for YRI and CEU respectively. 

By default, `dadi-cli` generates folded spectrum. To generate unfold spectrum, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

### Inferring demographic models

For inferring demographic models, we use the spectrum from the synonymous SNPs. Here, we use the `IM_pre` model. In this model, the ancestral population had an instantaneous change of population size before it diverged into two populations. After divergence, the two populations experienced exponential expansion. To find out the parameters of the `IM_pre` model, users can use `dadi-cli Model --names IM_pre`.

To start the inference, users should choose the initial value for each parameters with `--p0`, and specify the lower bounds and upper bounds for these parameters with `--lbounds` and `--ubounds`. Beside the eight parameters in the `IM_pre` model, we also use `--misid` to include a parameter measuring the proportion of alleles that their ancestral states are misidentified as the last parameter. Therefore, we have nine parameters in total. Because we need to run optimization several times to find out a coverged result with maximum likelihood, users can use `--jobs` to specify how many times of optimization will run parallelly.

    dadi-cli InferDM --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 1 1 .5 1 1 1 1 1 .5 --ubounds 10 10 1 10 10 10 10 10 1 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
After the optimization, users can use `BestFit` to obtain the best fit parameters.

    dadi-cli BestFit --dir ./examples/results/demo/optimization1/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 1 10 10 10 10 10 1 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
The result is

    NO CONVERGENCE: Likelihoods are not converged
    The maximum likelihood: -29932.010892115122
    The parameters with the maximum likelihood:
    1.8631877349945314      0.548573103499551       0.9612911219579375      3.438145697001221       4.391082674816054       0.09972864053502319  0.2939414026578067       0.2547625062911173      0.015493918178101734    6302.264966655559
    
As the result suggests, our optimization is not converged. Therefore, we need further optimization using the parameters with the maximum likelihood as the initial parameters.

    dadi-cli InferDM --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 1 10 10 10 10 10 1 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization2/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
After the optimization, we use `BestFit` again.

    dadi-cli BestFit --dir ./examples/results/demo/optimization2/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 1 10 10 10 10 10 1 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
The result is

    WARNING: The optimized parameters are close to the boundaries
    CONVERGED RESULT FOUND!
    The maximum likelihood: -29931.941978000257
    The best fit parameters:
    1.8597907391800936      0.5364664703406542      0.961215941903285       3.4123989204975254      4.3523495145830795      0.09951499748102086  0.2985451283565041       0.2564721142886847      0.015434829254785003    6328.564611583578
    
As the result suggests, our optimization is converged, and the best fit parameters are in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`. However, some parameters may be close to the boundaries. Users should be cautious and may increase the boundaries to examine whether these boundaries would affect the results significantly. The best fit parameters are shown in below. The first column is the likelihood corresponding to these parameters, and the last column is the population-scaled mutation rate of the synonymous SNPs.

| likelihood | nuPre | TPre | s | nu1 | nu2 | T | m12 | m21 | misid | theta |
| - | - | - | - | - | - | - | - | - | - | - |
| -29931.942 | 1.860 | 0.536 | 0.961 | 3.412 | 4.352 | 0.100 | 0.299 | 0.256 | 0.015 | 6328.565 |

### Generating caches for DFE inference

After inferring the best fit demographic model, users may also infer DFE from data. To perform DFE inference, users need to generate caches at first. Because we use the `IM_pre` model in the demographic inference, we need to use the same demographic model plus selection, the `IM_pre_sel_single_gamma` model or the `IM_pre_sel` model. The `IM_pre_sel` model is used for inferring DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `IM_pre_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations. The `IM_pre_sel_single_gamma` model can also be used for inferring DFE from a single population.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`. `--sample-size` defines the population size of each population. `--mp` indicates using multiprocess to accelerate the computation. The output is pickled and can access through the `pickle` module in `Python`.

    dadi-cli GenerateCache --model IM_pre_sel_single_gamma --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --sample-size 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --mp
    
    dadi-cli GenerateCache --model IM_pre_sel --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --misid --sample-sizes 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --mp

### Inferring DFE

For inferring DFE, we use the spectrum from the nonsynonymous SNPs and an example from inferring joint DFE<sup>2</sup>. In joint DFE inference, we need two caches. `--cache1d` accepts the cache that assumes the population-scaled selection coefficients are the same in the two populations. `--cache2d` accepts the cache that assumes the population-scaled selection coefficients are different in the two populations. Here, we define the marginal DFE is a lognormal distribution with `--pdf1d` and the joint DFE is a bivariate lognormal distribution with `--pdf2d`. In total, we have five parameters: the mean of the lognormal distribution, the standard deviation of the lognormal distribution, the correlation coefficient of the bivariate lognormal distribution, one minus the DFE correlation coefficienct, and the misidentification for the ancestral states. We fix the correlation coefficient in the bivariate lognormal distribution (the third parameter) to be zero with `--constants`. `-1` indicates there is no boundary or not fixed for a parameter. We use `--ratio` to specify the ratio of the nonsynonymous SNPs to the synonymous SNPs to calculate the population-scaled mutation rate of the nonsynonymous SNPs. 

    dadi-cli InferDFE --non-fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --misid --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1 --constants -1 -1 0 -1 -1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ratio 2.31 --output ./examples/results/dfe/optimization1/1KG.YRI.CEU.IM_pre.dfe.params --jobs 28

After the optimization, users can use `BestFit` to obtain the best fit parameters and save it in `./examples/results/dfe/varied_w/1KG.YRI.CEU.IM_pre.bestfit.dfe.params`.

    dadi-cli BestFit --dir ./examples/results/dfe/optimization1/ --output ./examples/results/dfe/varied_w/1KG.YRI.CEU.IM_pre.bestfit.dfe.params --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1
    
The result is

    WARNING: The optimized parameters are close to the boundaries
    CONVERGED RESULT FOUND!
    The maximum likelihood: -27880.30877335643
    The best fit parameters:
    2.114903459080246       4.913174122734687       0.0     0.005034967797548346    0.008922032850131625

Similar to the best fit parameters in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`, the first column is the likelihood.

| likelihood | mu | sigma | rho | 1 - w | misidentification |
| - | - | - | - | - | - |
| -27880.309 | 2.115  | 4.913  | 0.0  | 0.005  | 0.009 |

### Performing statistical testing

To performing statistical testing with the Godambe Information Matrix, users should first use `GenerateFs` to generate bootstrapping data from VCF files.

    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_syn/1KG.YRI.CEU.synonymous.snps.unfold
    
    dadi-cli GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/fs/bootstrapping_non/1KG.YRI.CEU.nonsynonymous.snps.unfold
    
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

- [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/)

## References

1. [Gutenkunst et al., *PLoS Genet*, 2009.](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000695)
2. [Huang et al., bioRixv, 2021.]()