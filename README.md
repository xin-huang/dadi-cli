# dadi-CLI

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE)
[![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)

`dadi-CLI` provides a command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/) to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data based on diffusion approximation. 

## Installation

To install `dadi-CLI`, users can use `conda`.

To get help information, users can use

    dadi-CLI -h

There are nine subcommands in `dadi-CLI`: 
- `GenerateFs`
- `GenerateCache`
- `InferDemography`
- `InferDFE`
- `BestFit` 
- `Stat`
- `Plot`
- `Model`
- `Pdf`

To display help information for each subcommand, users can use

    dadi-CLI subcommand -h
    
For example,

    dadi-CLI GenerateFs -h

## Usage: An Example

Here we use the data from the 1000 Genomes Project to demonstrate how to apply `dadi-CLI` in research.

### Generating allele frequency spectrum from VCF files

`dadi-CLI` only accepts VCF files to generate allele frequency spectrum. To generate the spectrum, users can use

    dadi-CLI GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --output ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs
    
    dadi-CLI GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --output ./examples/results/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs

Here `./examples/data/1KG.YRI.CEU.popfile.txt` is a file providing the population information for each individual. In the population information file, each line contains two fields. The first field is the name of the individual, and the second field is the name of the population that the individual belongs to. For example,

    NA12718	CEU
    NA12748	CEU
    NA12775	CEU
    NA19095	YRI
    NA19096	YRI
    NA19107	YRI

`--pop-ids` specifies the ID of the population. Here we have two populations YRI and CEU. The population IDs should match those listed in the population information file above.

`--projections` specifies the sample size of the population. Here we have 108 YRI individuals and 99 CEU individuals. Therefore, we have 216 and 198 haploidtypes for YRI and CEU respectively. 

By default, `dadi-CLI` generates folded spectrum. To generate unfold spectrum, users should add `--polarized` and the VCF files should have the `AA` in the `INFO` field to specify the ancestral allele for each SNP.

Users can also use `GenerateFs` to generate bootstrapping data from VCF files. These bootstrapping data will be used in the statistical testing with the Godambe Information Matrix.

    dadi-CLI GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.synonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/bootstrapping_syn/1KG.YRI.CEU.synonymous.snps.unfold.bootstrapping
    
    dadi-CLI GenerateFs --vcf ./examples/data/1KG.YRI.CEU.biallelic.nonsynonymous.snps.withanc.strict.vcf.gz --pop-info ./examples/data/1KG.YRI.CEU.popfile.txt --pop-ids YRI CEU --projections 216 198 --polarized --bootstrap 100 --chunk-size 1000000 --output ./examples/results/bootstrapping_non/1KG.YRI.CEU.nonsynonymous.snps.unfold.bootstrapping

### Inferring demographic models

For inferring demographic models, we use the spectrum from the synonymous SNPs.

    dadi-CLI InferDemography --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 1 1 .5 1 1 1 1 1 .5 --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
To obtain the best fit parameters, users can use

    dadi-CLI BestFit --dir ./examples/results/demo/optimization1/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
Therefore, we need further optimization. 

    dadi-CLI InferDemography --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 1.8631877349945314 0.548573103499551 0.9612911219579375 3.438145697001221 4.391082674816054 0.09972864053502319 0.2939414026578067 0.2547625062911173 0.015493918178101734 --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization2/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
After the optimization

    dadi-CLI BestFit --dir ./examples/results/demo/optimization2/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
Now we find our optimization is converged, and the best fit parameters are in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`.

### Generating caches for DFE inference

    dadi-CLI GenerateCache --model IM_pre_sel_single_gamma --demo-popt 1.8597907391800936 0.5364664703406542 0.961215941903285 3.4123989204975254 4.3523495145830795 0.09951499748102086 0.2985451283565041 0.2564721142886847 --sample-size 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --mp
    
    dadi-CLI GenerateCache --model IM_pre_sel --demo-popt 1.8597907391800936 0.5364664703406542 0.961215941903285 3.4123989204975254 4.3523495145830795 0.09951499748102086 0.2985451283565041 0.2564721142886847 --sample-sizes 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --mp

### Inferring DFE

For inferring DFE, we use the spectrum from the nonsynonymous SNPs.

### Performing statistical testing

### Plotting

`dadi-CLI` can plot allele frequency spectrum from data or compare the spectra between model and data.

To plot frequency spectrum from data, users can use

    dadi-CLI Plot --fs example.fs --output example.fs.pdf
    
To compare two frequency spectra from data, users can use

    dadi-CLI Plot --fs example1.fs --fs2 example2.fs --output example.fs.comparison.pdf
    
To compare frequency spectra between a demographic model without selection and data, users can use

    dadi-CLI Plot --fs example.fs 
    
To compare frequency spectra between a demographic model with selection and data, users can use

    dadi-CLI Plot --fs
    
### Available demographic models

`dadi-CLI` provides a subcommand `Model` to help users finding available demographic models in `dadi`.
To find out available demographic models, users can use

    dadi-CLI Model --names
    
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

    dadi-CLI Model --names IM
    
Then the detail of the model will be displayed in the screen:

    - IM:

            Isolation-with-migration model with exponential pop growth.
            Two populations in this model.

            params = [s,nu1,nu2,T,m12,m21]

                  s: Size of pop 1 after split (Pop 2 has size 1-s)
                nu1: Final size of pop 1 (in units of Na)
                nu2: Final size of pop 2 (in units of Na)
                  T: Time in the past of split (in units of 2*Na generations)
                m12: Migration from pop 2 to pop 1 (2*Na*m12)
                m21: Migration from pop 1 to pop 2 (2*Na*m21)

### Available DFE distributions

`dadi-CLI` provides a subcommand `Pdf` to help users finding available probability density functions for DFE inference in `dadi`.

To find out available probability density functions, users can use

    dadi-CLI Pdf --names
    
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

    dadi-CLI Pdf --names beta
    
Then the detail of the function will be displayed in the screen:

    - beta:

            Beta probability density function.

            params = [alpha, beta]

## Dependencies

- [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/)

## References

[Gutenkunst et al., *PLoS Genet*, 2009.](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000695)