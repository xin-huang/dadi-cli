# dadi.LowPass Integration

dadi-cli can utilize the [LowPass module of dadi](https://dadi.readthedocs.io/en/latest/user-guide/low-pass/). This enables the ability to correct models based on the coverage each sample has.

## GenerateFs Input

Before you use LowPass you'll want to make sure your VCF has the allele depth (AD) entry.
<pre>
FORMAT
GT:<b>AD</b>:DP:GQ:PL
</pre>
The information from the AD entry is used for generating a Demographic model. Users can save the information in a pickled dictionary when running `GenerateFs` with the `--calc-coverage`:
<pre><code>
dadi-cli GenerateFs --vcf examples/data/mus.syn.subset.vcf.gz --pop-info examples/data/mouse.popfile.txt --pop-ids Mmd_IRA Mmd_FRA --projections 4 8 --polarized --output examples/results/lowpass/mus.syn.fs <b>--calc-coverage</b>
dadi-cli GenerateFs --vcf examples/data/mus.nonsyn.subset.vcf.gz --pop-info examples/data/mouse.popfile.txt --pop-ids Mmd_IRA Mmd_FRA --projections 4 8 --polarized --output examples/results/lowpass/mus.nonsyn.fs <b>--calc-coverage</b>
</pre></code>
In addition to the `mus.syn.fs` and `mus.nonsyn.fs` SFS files, `mus.syn.fs.coverage.pickle` and `mus.nonsyn.fs.coverage.pickle` are generated. These files will be used for `InferDM` and `InferDFE` to preform the LowPass model correction.

## InferDM with LowPass

LowPass will correct the demographic and DFE models based on the coverage of samples, to use it users will need to use the `--coverage-model` flag, which `--coverage-model` takes the `.coverage.pickle` file and total number of haplotypes in the data for each population. There were 10 Mmd_IRA samples and 16 Mmd_FRA samples being requested from the `--pop-info` file from `GenerateFs`.
<pre><code>
dadi-cli InferDM --fs examples/results/lowpass/mus.syn.fs --model split_mig --p0 4.5 0.8 0.8 0.36 0.01 --lbounds 1e-5 1e-5 1e-5 1e-5 1e-5 --ubounds 10 10 1 10 1 --output-prefix examples/results/lowpass/mus.split_mig.lowpass --optimizations 20 --check-convergence 5 --grids 50 60 70 <b>--coverage-model examples/results/lowpass/mus.syn.fs.coverage.pickle 10 16<b>
</pre></code>

There are no extra parameters for the LowPass model correction, so results can look similar to non-LowPass corrected results.

## InferDFE with LowPass

InferDFE is largely the same as InferDM. When users run `GenerateCache`, user's will want to use the number of haplotypes in the data for `--sample-sizes` instead of the sample sizes in the SFS file. Given that there were 10 Mmd_IRA samples and 16 Mmd_FRA haplotypes users would use `--sample-sizes 10 16` instead of `--sample-sizes 4 8`:
<pre><code>
dadi-cli GenerateCache --model split_mig_sel_single_gamma <b>--sample-sizes 10 16</b> --grids 50 60 70 --gamma-pts 20 --gamma-bounds 1e-4 100 --demo-popt examples/results/lowpass/mus.split_mig.lowpass.InferDM.bestfits --output examples/results/lowpass/mus.1d.cache
</pre></code>

When users run InferDFE they should use the `--coverage-model` flag with the similar inputs as `InferDM`, except using the `.coverage.pickle` file for the nonsynonymous data.
<pre><code>
dadi-cli InferDFE --fs examples/results/lowpass/mus.nonsyn.fs --demo-popt examples/results/lowpass/mus.split_mig.lowpass.InferDM.bestfits --cache1d examples/results/lowpass/mus.1d.cache --pdf1d lognormal --ratio 2.31 --p0 1 1 0.01 --lbounds 1e-5 1e-5 1e-5 --ubounds 30 10 1 --optimizations 20 --check-convergence 5 --output-prefix examples/results/lowpass/mus.lognormal.lowpass <b>--coverage-model examples/results/lowpass/mus.nonsyn.fs.coverage.pickle 10 16</b>
</pre></code>