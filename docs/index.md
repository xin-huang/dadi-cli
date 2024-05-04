# dadi-cli

`dadi-cli` provides a robust and user-friendly command line interface for [dadi](https://dadi.readthedocs.io)<sup>1</sup> to help users to quickly apply `dadi` to their research. `dadi` is a flexible python package for inferring demographic history and the distribution of fitness effects (DFE) from population genomic data. However, using `dadi` requires knowledge of python and patience to tune different models.

## Requirements

`dadi-cli` works on UNIX/LINUX operating systems and tested with the following:

- Python 3.9 and 3.10
- Python packages:
	- cuda
	- cyvcf2
	- dadi > 2.1.0
	- demes
	- dill
	- matplotlib
	- ndcctools
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
	mamba activate dadi-cli-cpu

To get help information, users can use

```         
dadi-cli -h
```

There are thirteen subcommands in `dadi-cli`:

| Command | Description |
| - | - |
| GenerateFs    | Generate frequency spectrum from VCF files. |
| GenerateCache | Generate selection coefficient cache for inferring DFE. |
| SimulateDM    | Generate frequency spectrum based on a demographic history. |
| SimulateDFE   | Generate frequency spectrum based on a DFE. |
| SimulateDemes | Generate frequency spectrum based on a Demes .yml file. |
| InferDM       | Infer a demographic models from an allele frequency spectrum. |
| InferDFE      | Infer distribution of fitness effects from frequency spectrum. |
| Plot          | Plot 1D/2D/3D frequency spectrum. |
| StatDM        | Perform statistical tests using Godambe Information Matrix for demographic models. |
| StatDFE       | Perform statistical tests using Godambe Information Matrix for DFEs. |
| BestFit       | Obtain the best fit parameters. |
| Model         | Display available demographic models. |
| Pdf           | Display available probability density functions for distribution of fitness effects. |

To display help information for each subcommand, users can use the `-h` option. For example,

```         
dadi-cli GenerateFs -h
```

In this manual, we use the data from the 1000 Genomes Project and data simulated with `dadi-cli` to demonstrate how to apply `dadi-cli` in research. Users could also refer to [the dadi manual](https://dadi.readthedocs.io/en/latest/) for more details on parameters in `dadi`.

## Overview

The overview of the workflow implemented in `dadi-cli` is shown below:

![dadi-cli-workflow]()
