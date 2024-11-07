# dadi.LowPass Integration

dadi-cli can utilize the LowPass module of dadi (url). This enables the ability to correct models based on the coverage each sample has.

## GenerateFs Input

Before you use LowPass you'll want to make sure your VCF has the allele depth (AD) entry.
<pre>
FORMAT
GT:<b>AD</b>:DP:GQ:PL
</pre>
The information from the AD entry is used for generating a Demographic model. Users can save the information in a pickled dictionary when running `GenerateFs` with the `--calc-coverage`.
<pre>
dadi-cli GenerateFs --vcf examples/data/mus.syn.subset.vcf.gz --pop-info examples/data/mouse.popfile.txt --pop-ids Mmd_IRA Mmd_FRA --projections 4 8 --polarized --output examples/results/lowpass/mus.syn.fs <b>--calc-coverage</b>
dadi-cli GenerateFs --vcf examples/data/mus.nonsyn.subset.vcf.gz --pop-info examples/data/mouse.popfile.txt --pop-ids Mmd_IRA Mmd_FRA --projections 4 8 --polarized --output examples/results/lowpass/mus.nonsyn.fs <b>--calc-coverage</b>
</pre>
In addition to the `mus.fs` SFS file, an additional file `mus.syn.fs.coverage.pickle` is generated, which will be used for `InferDM`.

## InferDM with LowPass
LowPass will correct the demographic and DFE models based on the coverage of samples, to use it users will need to use the `--coverage-model` flag.
<pre>
dadi-cli InferDM --fs examples/results/lowpass/mus.syn.fs --model split_mig --p0 4.5 0.8 0.8 0.36 0.01 --lbounds 1e-5 1e-5 1e-5 1e-5 1e-5 --ubounds 10 10 1 10 1 --output-prefix examples/results/lowpass/mus.split_mig.lowpass --optimizations 20 --check-convergence 5 --grids 50 60 70 <b>--coverage-model examples/results/lowpass/mus.syn.fs.coverage.pickle 10 16<b>
</pre>
`--coverage-model` takes the `.coverage.pickle` file and total number of samples in the data for each population. Here there were 10 Mmd_IRA samples and 16 Mmd_FRA samples being requested from the `--pop-info` file from `GenerateFs`.

There are no extra parameters for the LowPass model correction, so results can look similar to non-LowPass results.

## InferDFE with LowPass

InferDFE is largely the same as InferDM. When users run GenerateCache, nothing extra needs to be done.
```
dadi-cli GenerateCache --model split_mig_sel_single_gamma --sample-sizes 4 8 --grids 50 60 70 --gamma-pts 20 --gamma-bounds 1e-4 100 --demo-popt examples/results/lowpass/mus.split_mig.lowpass.InferDM.bestfits --output examples/results/lowpass/mus.1d.cache
```

When users run InferDFE they should use the `--coverage-model` flag with the similar inputs, except using the `.coverage.pickle` file for the nonsynonymous data.
```
dadi-cli InferDFE --fs examples/results/lowpass/mus.nonsyn.fs --demo-popt examples/results/lowpass/mus.split_mig.lowpass.InferDM.bestfits --cache1d examples/results/lowpass/mus.1d.cache --pdf1d lognormal --ratio 2.31 --p0 1 1 0.01 --lbounds 1e-5 1e-5 1e-5 --ubounds 30 10 1 --optimizations 20 --check-convergence 5 --output-prefix examples/results/lowpass/mus.lognormal.lowpass <b>--coverage-model examples/results/lowpass/mus.nonsyn.fs.coverage.pickle 10 16</b>
```