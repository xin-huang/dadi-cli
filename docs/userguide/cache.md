# Generating caches for DFE inference

After inferring a best fit demographic model, users may also infer distributions of fitness effects (DFEs) from data. To perform DFE inference, users need to first generate of cache of frequency spectra. Because we use the `split_mig` model in the demographic inference, we need to use the same demographic model plus selection, the `split_mig_sel` model or the `split_mig_sel_single_gamma` model. The `split_mig_sel` model is used for inferring the DFE from two populations by assuming the population-scaled selection coefficients are different in the two populations, while the `split_mig_sel_single_gamma` model assumes the population-scaled selection coefficients are the same in the two populations.

Here, `--model` specifies the demographic model plus selection used in the inference. `--demo-popt` specifies the demographic parameters, which are stored in `./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits`. `--sample-size` defines the population size of each population. The output is pickled and can access through the `pickle` module in `Python`. By default `GenerateCache` will make the cache for the situation where the selection coefficients are the same in the two populations. If users want to to make the cache for the situation where the selection coefficients are independent from one another, they should use the `--dimensionality 2` option. Users can use the `--gamma-bounds` option to choose the range of the gamma distribution and the `--gamma-pts` option can be used to specify the number of selection coefficients that will be selected in that range to generate the cache. Note that the higher (more negative) you make the `--gamma-bounds`, the bigger the grid points, altered via the `--grids` option, users will want to use.

Here is an example command to generate a cache with shared selection coefficients:
```
dadi-cli GenerateCache --model split_mig_sel_single_gamma --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --cpus 4
```
Here is an example command to generate a cache with independent selection coefficients:
```
dadi-cli GenerateCache --model split_mig_sel --dimensionality 2 --demo-popt ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.params.InferDM.bestfits --sample-size 20 20 --grids 60 80 100 --gamma-pts 10 --gamma-bounds 1e-4 200 --output ./examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.spectra.bpkl --cpus 4
```
Users will likely want to use larger `--gamma-bounds` and `--gamma-pts` than the example.