# dadi-cli

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://dadi.readthedocs.io)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data. However, using `dadi` requires knowledge of python and patience to tune different models.

## Requirements

`dadi-cli` works on UNIX/LINUX operating systems and tested with the following:

- Python 3.8
- Python packages:
	- dadi > 2.1.0
	- demes
	- dill == 0.3.4
	- matplotlib
	- ndcctools == 7.4.3
	- nlopt
	- numpy
	- pycuda
	- scipy
	- scikit-cuda

## Installation

Users can install dadi-cli through Conda Forge:
```
conda install -c conda-forge dadi-cli
```

Or, for the latest updates, clone this repo and using the following command

```         
python setup.py install
```

To get help information, users can use

```         
dadi-cli -h
```

There are thirteen subcommands in `dadi-cli`: 
- `GenerateFs` 
- `GenerateCache` 
- `InferDM` 
- `InferDFE` 
- `BestFit` 
- `StatDM` 
- `StatDFE` 
- `Plot` 
- `SimulateDM` 
- `SimulateDFE` 
- `SimulateDemes` 
- `Model` 
- `Pdf`

To display help information for each subcommand, users can use `-h`. For example,

```         
dadi-cli GenerateFs -h
```
