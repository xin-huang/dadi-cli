# dadi-cli

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://dadi.readthedocs.io)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data. However, using `dadi` requires knowledge of python and patience to tune different models.

## Requirements

`dadi-cli` works on UNIX/LINUX operating systems and tested with the following:

- Python 3.8
- Python packages:
	- cuda
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

Only [NVIDIA](https://www.nvidia.com) GPUs are supported if users want to accelerate their inference with GPUs.

## Installation

Users can install `dadi-cli` through [conda-forge](https://conda-forge.org/):
```
conda install -c conda-forge dadi-cli
```

Or, for the latest updates, clone this repo and using the following command

```         
pip install .
```

Users can also use `conda` to create a virtual environment and install the latest `dadi-cli` with these two conda environment files [conda-cpu-env.yml](https://github.com/xin-huang/dadi-cli/blob/master/conda-cpu-env.yml) and [conda-gpu-env.yml](https://github.com/xin-huang/dadi-cli/blob/master/conda-gpu-env.yml) in this repo. To install `conda`, please follow the [instruction](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). We recommend users install and use [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) via `mambaforge` or `miniforge` to create the virtual environment, because `mamba` is much faster than `conda`. Then users can use the following commands:

	mamba env create -f conda-cpu-env.yml
	conda activate dadi-cli-cpu

To get help information, users can use

```         
dadi-cli -h
```

There are thirteen subcommands in `dadi-cli`:

- GenerateFs 
- GenerateCache 
- InferDM 
- InferDFE 
- BestFit 
- StatDM 
- StatDFE 
- Plot 
- SimulateDM 
- SimulateDFE 
- SimulateDemes 
- Model 
- Pdf

To display help information for each subcommand, users can use the `-h` option. For example,

```         
dadi-cli GenerateFs -h
```

In this manual, we use the data from the 1000 Genomes Project and data simulated with `dadi-cli` to demonstrate how to apply `dadi-cli` in research.
