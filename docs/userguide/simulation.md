# Simulation

`dadi-cli` can simulate frequence spectra based on dadi demography or DFE code or on [Demes](https://popsim-consortium.github.io/demes-spec-docs/main/introduction.html) YMAL files with two subcommands: `SimulateDM` and `SimulateDFE`.

For example, users can simulate the AFS of a single population with a two-epoch demographic model using the following command:
```bash
dadi-cli SimulateDM --model two_epoch 
  --sample-sizes 20 --p0 10 0.1 --nomisid 
  --output two_epoch.simDM.fs
```
Here, the `--p0` argument specifies the values for the two demographic parameters in the two-epoch model, and the `--nomisid` argument tells dadi-cli exclude the parameter for the ancestral allele misidentification during the simulation.



Users can simulate the AFS of a single population with a two-epoch demographic model using the following command:
```bash
dadi-cli SimulateDM --model two_epoch 
  --sample-sizes 20 --p0 10 0.1 --nomisid 
  --output two_epoch.simDM.fs
```
A file with the simulated demography `two_epoch.simDM.fs` will be produced. 

If users want to generate caches and simulate a DFE based on a simulated demography, users can include `--inference-file` which will produce a file based on the text passed in `--output`, ex the command
```bash
dadi-cli SimulateDM --model three_epoch 
  --sample-sizes 20 --p0 10 5 0.02 0.1 
  --nomisid --output three_epoch.simDM.fs --inference-file
```
will produce the frequency spectrum `three_epoch.simDM.fs` and the optimization file `three_epoch.simDM.fs.SimulateDM.pseudofit`.

Users can also simulate the AFS with a DFE model, if they have a cache file from the `GenerateCache` subcommand. For example, if users had the cache from the [DFE Inference guide](https://dadi-cli.readthedocs.io/en/latest/userguide/dfe/#generating-caches-for-dfe-inference), they can run:
```
dadi-cli SimulateDFE --cache1d 1KG.YRI.CEU.20.split_mig.sel.single.gamma.spectra.bpkl 
  --pdf1d lognormal --ratio 2.31 --p0 2 4 --nomisid 
  --output lognormal.split_mig.simDFE.fs
```

Users can also simulate demography frequency spectrum with a Demes YAML file. To simulate with Demes, users will need to install it:
```
pip install demes
```

An [example Demes file](https://github.com/popsim-consortium/demes-python/tree/main/examples) `gutenkunst_ooa.yml` is below: 
```
description: The Gutenkunst et al. (2009) OOA model.
doi:
- https://doi.org/10.1371/journal.pgen.1000695
time_units: years
generation_time: 25

demes:
- name: ancestral
  description: Equilibrium/root population
  epochs:
  - {end_time: 220e3, start_size: 7300}
- name: AMH
  description: Anatomically modern humans
  ancestors: [ancestral]
  epochs:
  - {end_time: 140e3, start_size: 12300}
- name: OOA
  description: Bottleneck out-of-Africa population
  ancestors: [AMH]
  epochs:
  - {end_time: 21.2e3, start_size: 2100}
- name: YRI
  description: Yoruba in Ibadan, Nigeria
  ancestors: [AMH]
  epochs:
  - start_size: 12300
- name: CEU
  description: Utah Residents (CEPH) with Northern and Western European Ancestry
  ancestors: [OOA]
  epochs:
  - {start_size: 1000, end_size: 29725}
- name: CHB
  description: Han Chinese in Beijing, China
  ancestors: [OOA]
  epochs:
  - {start_size: 510, end_size: 54090}

migrations:
- {demes: [YRI, OOA], rate: 25e-5}
- {demes: [YRI, CEU], rate: 3e-5}
- {demes: [YRI, CHB], rate: 1.9e-5}
- {demes: [CEU, CHB], rate: 9.6e-5}
```
Users can simulate the AFS of YRI with the above Demes file and the following command:
```bash
dadi-cli SimulateDemes --demes-file gutenkunst_ooa.yml 
  --pop-ids YRI --sample-sizes 30 --output ooa.YRI.30.fs
```

Users can learn more about making Demes YAML files [here](https://popsim-consortium.github.io/demes-spec-docs/main/tutorial.html).
