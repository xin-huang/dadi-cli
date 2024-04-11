# Cloud computing

## Using Work Queue for distributed inference with dadi-cli

`dadi-cli`'s subcommands `InferDM` and `InferDFE` have built in options to work with [Cooperative Computing Tools (`CCTools`)](https://cctools.readthedocs.io/en/stable/about/) `Work Queue`, which facilitates launching independent optimizations across multiple machines, through several workload managers. 
To use `Work Queue`, users can use conda to install the required packages:

``` bash
conda install -c conda-forge dill ndcctools
```
Or go to the [CCTools Documentation](https://cctools.readthedocs.io/en/stable/install/) for more installation instructions. 
Note that CCTools is only avalible for Mac and Linux computers.

This example has been tested for submitting jobs to a `SLURM Workload Manager`. 
First we want to submit a factory to SLURM:
```bash
slurm_submit_workers -M dminf -P pwfile  -p '--time=00:10:00 --nodes=1 --ntasks=1' 5 --workers-per-cycle=0 --cores=1
```

`dminf` is the project name and `pwfile` is a file containing a password, both of which are needed for `dadi-cli` use. They can be passed into `dadi-cli` with the `--work-queue` flag, where users pass in the project name and then the password file. `--workers-per-cycle` can be set to zero, as `dadi-cli`'s `--optimizations` argument will determine the total number of workers requested from the factory. `--cores` controls how many CPUs each worker use and can be set to 1, as each worker will preform a singular optimization. 

Next users will want to submit jobs from `dadi-cli`:
```bash
dadi-cli InferDM --fs 1KG.YRI.CEU.20.syn.fs --model split_mig
  --lbounds 1e-3 1e-3 0 0 0 --ubounds 10 10 1 10 0.5 --force-convergence 10
  --output 1KG.YRI.CEU.20.split_mig
  --work-queue dminf pwfile
```
`dadi-cli` will send the number of workers as the number of optimizations you request. The `check-convergence` and `force-convergence` options work with `Work Queue` as well.

If users want to use another batch system with Work Queue, there are similar commands for Condor, SGE, PBS, and Torque found under [Worker Submission Scripts](https://cctools.readthedocs.io/en/latest/man_pages/). 
Users can also try to submit a [`work_queue_factory`](https://cctools.readthedocs.io/en/latest/man_pages/work_queue_factory/), which allows for automation of workers but can require more CPUs when requesting a large number of optimizations with `dadi-cli`.

## Terraform cloud computing for dadi-cli

### Setup Terraform

The [`dadi-cli` GitHub source code](https://github.com/xin-huang/dadi-cli) comes with a folder called `terraform` ([here](https://github.com/xin-huang/dadi-cli/tree/master/terraform)), which containes scripts users can use to launch Amazon Web Services (AWS) Elastic Clompute Cloud (EC2) instances to remotely run `dadi-cli` and `Work Queue`. 
Users will need to install [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) and the [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). 
If users have not already signed up for AWS and gotten an access key ID and secret access key, more information can be found [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html).

Users will need to create an SSH Key to connect Terraform:
```bash
ssh-keygen -f ssh-key
```
The above command will create a private SSH Key file "ssh-key" and a public SSH Key file "ssh-key.pub". 

### Terraform variables file

Users will need to edit the Terraform variables file, ["dadi.auto.tfvars" template](https://github.com/xin-huang/dadi-cli/blob/master/terraform/dadi.auto.tfvars), to setup Terraform to connect to AWS and run `dadi-cli` and work queue. 

In the ".tfvars" file, to setup AWS users can change choose the [instance_type](https://aws.amazon.com/ec2/instance-types/) and the region, and add the content of the public SSH Key file (lines 4, 7, and 10 of the template).
If users want to run `dadi-cli`, set `run = true` (line 15) and fill in the "parameters" (line 22) with the `dadi-cli` subcommand (`dadi-cli` command minus `dadi-cli` portion) the user wants to run. 
Users will want to include any data they will use in the "uploads" folder, which will be placed in the directory that `dadi-cli` is executed from.
If users want to fit a model to a frequency spectrum, "experimental-data.fs", they place in the "uploads" folder, they would fill the following for "parameters" in the ".tfvars" file:
```bash
parameters = InferDM --fs uploads/experimental-data.fs --model two_epoch --p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --grids 30 40 50 --output terra.two_epoch.demog.params --optimizations 2 --nomisid
```
To get results, users will need to SSH into the AWS instances Terraform launches. An easy way to SSH into the AWS instance is, from inside the "terraform" folder, to run:
```bash
ssh dadi@$(terraform output -raw public_ip) -i ssh-key
```

If users want to run work_queue_factory on an AWS instance, set `run = true` (line 27), and fill in the `project_name` (line 31) and `workqueue_password` (line 34). This can be ran independently if users want Terraform to launch an AWS instance to be a dedicated work queue factory.

If users named the SSH Key something besides "ssh-key" or if it is in a different directory than the "terraform" folder, line 129 in "main.tf", `private_key = "${file("ssh-key")}"`, will need to be edited to the PATH and file name.

Users might get an error if the requested region has too many instances running:
```consol
Error: error creating EC2 VPC: VpcLimitExceeded: The maximum number of VPCs has been reached.
```

## Cacao cloud computing for dadi-cli

Another resource for cloud computing with `dadi-cli` is the University of Arizona CyVerse's [Cacao](http://cacao.jetstream-cloud.org/), which provides a convinient GUI for launching instances to run `dadi-cli` and work queue factories. Cacao is built on Jetstream2, and users will need an account with [Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support (ACCESS)](https://access-ci.org/) and register for allocation.

A step-by-step guide for getting started on Cacao can be found [here](https://docs.jetstream-cloud.org/ui/cacao/getting_started/#1-login-to-cacao). For researchers that need more out of Cacao/Jetstream2, an overview of ACCESS can be found [here](https://allocations.access-ci.org/get-started-overview) and information on allocating resources for Jetstream2 can be found [here](https://docs.jetstream-cloud.org/alloc/overview/).

Once the user has access to Cacao, they can go to "Deployments" > "Add Deployment" > "launch a DADI OpenStack instance" and choose a region. 
If users want the instance to automatically run `dadi-cli` after it launches, they will need to fill in the `dadi-cli` subcommand in "Parameters". There is no easy way for users to upload frequency spectrum, as such `dadi-cli` can read https links that contain raw text data for the frequency spectrum, ex. https://tinyurl.com/u38zv4kw.
Users can also launch instances that run a work queue factory with or without `dadi-cli`, as such users can run one instance as a work queue factory and another instance running `dadi-cli` with work queue.

Notably, while direct frequency spectrum uploads are limited, dadi-cli can interpret raw text data from HTTPS links, such as links to raw text files uploaded to a [GitHub repository](https://github.com/) or [GitHub Gist](https://gist.github.com/). 
Flexibility is paramount, as users can deploy instances to function exclusively as a Work Queue factory or run in tandem with dadi-cli. 
For results, users can access the Cacao deployment Webshell or Webdesktop or SSH into their instance, provided they have shared a public ssh-key under credentials.

Users can access results via the Cacao deployment's Webshell or Webdesktop. If users provide a public ssh-key under [credentials](https://cacao.jetstream-cloud.org/credentials), they can also ssh into the instance with:
```
ssh USERNAME@PUBLIC_IP -i SSHKEY
```
Where `USERNAME` is the username for Cacao, `PUBLIC_IP` is the public IP of the deployment, and `SSHKEY` is the file that contains the private ssh-key information paired with the public key used for the deployment.


## Snakemake

Finally, as a command-line tool, dadi-cli is straightforward to integrate within workflow managers like [Snakemake](https://snakemake.readthedocs.io/en/stable/). 
For example, we provide a [Snakemake workflow](https://github.com/xin-huang/dadi-cli-analysis/tree/main/workflows) that fits DFE models to all populations within the 1000 Genomes Project data. 
This also allows for efficient cloud computing through Snakemake across diverse platforms, including Google Cloud Life Sciences and Azure Batch.
