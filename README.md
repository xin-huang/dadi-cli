# dadi-CLI

[![license](https://img.shields.io/badge/license-Apache%202.0-red.svg)](LICENSE)
[![language](http://img.shields.io/badge/language-python-blue.svg)](https://www.python.org/)

`dadi-CLI` provides a command line interface for [dadi](https://bitbucket.org/gutenkunstlab/dadi/src/master/) to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data based on diffusion approximation. 

## Installation

To install `dadi-CLI`, users can use `conda`.

    conda install -c conda-forge dadi-CLI

To get help information, users can use

    dadi-CLI -h

There are nine subcommands in `dadi-CLI`: 
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

    dadi-CLI InferDM --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 1 1 .5 1 1 1 1 1 .5 --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization1/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
To obtain the best fit parameters, users can use

    dadi-CLI BestFit --dir ./examples/results/demo/optimization1/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
As the results suggest, our optimization is not converged. Therefore, we need further optimization using the parameters with the maximum likelihood as the initial parameters.

    dadi-CLI InferDM --syn-fs ./examples/results/1KG.YRI.CEU.synonymous.snps.unfold.fs --model IM_pre --misid --p0 ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5 --output ./examples/results/demo/optimization2/1KG.YRI.CEU.IM_pre.demo.params --jobs 28
    
After the optimization, we use `dadi-CLI BestFit` again.

    dadi-CLI BestFit --dir ./examples/results/demo/optimization2/ --output ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ubounds 10 10 0.999 10 10 10 10 10 0.99999 --lbounds 10e-3 0 10e-3 10e-3 10e-3 0 0 0 10e-5
    
As the results suggest, our optimization is converged, and the best fit parameters are in `./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params`. However, some parameters may be close to the boundaries. Users should be cautious and may increase the boundaries to examine whether these boundaries would affect the results significantly. The meaning of each parameter is shown in below.

| Likelihood | theta |
| - | - |
| -29931.941978000257 | 6328.564611583578 |

To find out the parameters of the `IM_pre` model, users can use `dadi-CLI Model --names IM_pre`.

### Generating caches for DFE inference

    dadi-CLI GenerateCache --model IM_pre_sel_single_gamma --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --sample-size 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --mp
    
    dadi-CLI GenerateCache --model IM_pre_sel --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --sample-sizes 216 198 --output ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --mp

### Inferring DFE

For inferring DFE, we use the spectrum from the nonsynonymous SNPs.

    dadi-CLI InferDFE --non-fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --misid --constants -1 -1 0 -1 -1 --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ratio 2.31 --output ./examples/results/dfe/varied_w/optimization1/1KG.YRI.CEU.IM_pre.dfe.params --jobs 28

    dadi-CLI BestFit --dir ./examples/results/dfe/optimization1/ --output ./examples/results/dfe/varied_w/1KG.YRI.CEU.IM_pre.bestfit.dfe.params --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1
    
    dadi-CLI InferDFE --non-fs ./examples/results/fs/1KG.YRI.CEU.nonsynonymous.snps.unfold.fs --cache1d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.single.gamma.spectra.bpkl --cache2d ./examples/results/caches/1KG.YRI.CEU.IM_pre.sel.spectra.bpkl --misid --constants -1 -1 0 0 -1 --pdf1d lognormal --pdf2d biv_lognormal --p0 1 1 0 .5 .5 --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1 --demo-popt ./examples/results/demo/1KG.YRI.CEU.IM_pre.bestfit.demo.params --ratio 2.31 --output ./examples/results/dfe/fixed_w/optimization1/1KG.YRI.CEU.IM_pre.dfe.params --jobs 28
    
    dadi-CLI BestFit --dir ./examples/results/dfe/optimization1/ --output ./examples/results/dfe/fixed_w/1KG.YRI.CEU.IM_pre.bestfit.dfe.params --lbounds -1 0.01 0 0 0 --ubounds -1 -1 1 1 1

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

1. [Gutenkunst et al., *PLoS Genet*, 2009.](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1000695)
2. [Huang et al., bioRixv, 2021]()