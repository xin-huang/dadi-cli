# Simulation

Users can simulate frequence spectra based on dadi demography or DFE code or on [Demes](https://popsim-consortium.github.io/demes-spec-docs/main/introduction.html) YMAL files.

`dadi-cli` can simulate dadi demography with `dadi-cli SimulateDM`. Users need to pass in a `--model` (and `--model-file` if it is a custom model), `--sample-sizes`, parameters for the model (`--p0`), and spectrum file name (`--output`). Running
```
dadi-cli SimulateDM --model two_epoch --sample-sizes 20 --p0 10 0.1 --nomisid --output two_epoch.simDM.fs
```
Will produce a file with the simulated demography `two_epoch.simDM.fs`. If users want to generate caches and simulate a DFE based on a simulated demography, users can include `--inference-file` which will produce a file based on the text passed in `--output`, ex the command
```
dadi-cli SimulateDM --model three_epoch --sample-sizes 20 --p0 10 5 0.02 0.1 --nomisid --output three_epoch.simDM.fs --inference-file
```
will produce the frequency spectrum `three_epoch.simDM.fs` and the optimization file `three_epoch.simDM.fs.SimulateDM.pseudofit`.

Users can also simulate demography frequency spectrum with Demes. To simulate with Demes, users will need to install it:
```
pip install demes
```
When users have a [Demes YAML file](https://popsim-consortium.github.io/demes-spec-docs/main/tutorial.html) made, they can simulate frequency spectra that is readable by dadi:
```
dadi-cli SimulateDemes --demes-file examples/data/gutenkunst_ooa.yml --pop-ids YRI --sample-sizes 30 --output ooa.YRI.30.fs
```
A file, `ooa.YRI.30.fs`, with the spectrum will be made.

Users can simulate a DFE frequency spectrum if they have the caches (`--cache1d` and/or `--cache2d`). Users will also need to define the PDF(s) (`--pdf1d` and/or `--pdf2d`), the `--ratio` of nonsynonymous to synonymous mutation rate, and the file name (`--output`). Running:
```
dadi-cli SimulateDFE --cache1d examples/results/caches/1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl --pdf1d lognormal --ratio 2.31 --p0 2 4 --nomisid --output lognormal.split_mig.simDFE.fs
```
will produce a frequency spectrum file based on a lognormal DFE, `lognormal.split_mig.simDFE.fs`.
