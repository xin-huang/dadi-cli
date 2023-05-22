# Cloud computing

## Using Work Queue for distributed inference with dadi-cli

`dadi-cli`'s subcommands `InferDM` and `InferDFE` have built in options to work with Cooperative Computing Tools (`CCTools`)'s `Work Queue` for launching independent optimizations across multiple machines. To use `Work Queue`, users can use conda to install the required packages:

``` bash
conda install -c conda-forge dill ndcctools
```
Or go to the [CCTools Documentation](https://cctools.readthedocs.io/en/stable/install/). CCTools is only avalible for Mac and Linux computers.

This example has been tested for submitting jobs to a `Slurm Workload Manager`. First we want to submit a factory.

```bash
work_queue_factory -T local -M dm-inference -P ./tests/mypwfile --workers-per-cycle=0 --cores=1
```

`dm-inference` is the project name and `mypwfile` is a file containing a password, both of which are needed for `dadi-cli` use. They can be passed into `dadi-cli` with the `--work-queue` flag, where users pass in the project name and then the password file. `--workers-per-cycle` can be set to zero, as `dadi-cli`'s `--optimizations` argument will determine the total number of workers requested from the factory. `--cores` controls how many CPUs each worker use and can be set to 1, as each worker will preform a singular optimization. Next users will want to submit jobs from `dadi-cli`. By default, `work_queue_factory` will request as many CPUs as avalible, users can control the number of CPUs used by controling the number of workers with `work_queue_factory`'s `--min-workers` and `--max-workers` arguments.

```bash
dadi-cli InferDM --fs ./examples/results/fs/1KG.YRI.CEU.20.synonymous.snps.unfold.fs --model split_mig --p0 1 1 .5 1 .5 --ubounds 10 10 1 10 1 --lbounds 10e-3 10e-3 10e-3 10e-3 10e-5 --grids 60 80 100 --output ./examples/results/demog/1KG.YRI.CEU.20.split_mig.demog.work_queue.params --optimizations 5 --maxeval 200 --check-convergence 5 --work-queue dm-inference ./tests/mypwfile
```

`dadi-cli` will send the number of workers as the number of optimizations you request. The `check-convergence` and `force-convergence` options work with `Work Queue` as well.

## Terraform cloud computing for dadi-cli

The `dadi-cli` GitHub source code comes with a folder called `terraform`, which containes scripts users can use to launch Amazon Web Services (AWS) Elastic Clompute Cloud (EC2) instances to remotely run `dadi-cli` and `Work Queue`. Users will need to install [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) and the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). If users have not already signed up for AWS and gotten an access key ID and secret access key, more information can be found [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html).

Users will need to create an SSH Key to connect Terraform:
```bash
ssh-keygen -f ssh-key
```
The above command will create a private SSH Key file "ssh-key" and a public SSH Key file "ssh-key.pub".
Users will need to edit the "dadi.auto.tfvars" to setup Terraform to connect to AWS and run `dadi-cli` and work queue. 

For AWS, users need to choose the [instance_type](https://aws.amazon.com/ec2/instance-types/), the region, and the content of the public SSH Key file.
If users want to run `dadi-cli`, set `run = true` and fill in the "parameters" with the `dadi-cli` subcommand (`dadi-cli` command minus `dadi-cli` portion) the user wants to run. Ex:
```bash
InferDM --fs two_epoch_syn.fs --model two_epoch --p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --grids 30 40 50 --output terra.two_epoch.demog.params --optimizations 2 --nomisid
```
Users will want to include any data they will use in the "uploads" folder, which will be placed in the directory that `dadi-cli` is executed from.
To get results, users will need to SSH into the AWS instances Terraform launches. An easy way to SSH into the AWS instance is, from inside the "terraform" folder, to run:
```bash
ssh dadi@$(terraform output -raw public_ip) -i ssh-key
```

If users want to run work_queue_factory on an AWS instance, set `run = true`, and fill in the `project_name` and `workqueue_password`. This can be ran independently if users want Terraform to launch an AWS instance to be a dedicated work queue factory.

If users named the SSH Key something besides "ssh-key" or if it is in a different directory than the "terraform" folder, line 129 in "main.tf", `private_key = "${file("ssh-key")}"`, will need to be edited to the PATH and file name.

```consol
Error: error creating EC2 VPC: VpcLimitExceeded: The maximum number of VPCs has been reached.
```
Means that the requested region has too many instances running.


## Cacao cloud computing for dadi-cli

Another resource for cloud computing with `dadi-cli` is the University of Arizona CyVerse's [Cacao](http://cacao.jetstream-cloud.org/), which provides a convinient GUI for launching instances to run `dadi-cli` and work queue factories. Cacao is built on Jetstream2, and users will need an account with Advanced Cyberinfrastructure Coordination Ecosystem: Services & Support (ACCESS) and register for allocation.

A step-by-step guide for getting started on Cacao can be found [here](https://docs.jetstream-cloud.org/ui/cacao/getting_started/#1-login-to-cacao). For researchers that need more out of Cacao/Jetstream2, an overview of ACCESS can be found [here](https://allocations.access-ci.org/get-started-overview) and information on allocating resources for Jetstream2 can be found [here](https://docs.jetstream-cloud.org/alloc/overview/).

Once the user has access to Cacao, they can go to "Deployments" > "Add Deployment" > "launch a DADI OpenStack instance" and choose a region. 
If users want the instance to automatically run `dadi-cli` after it launches, they will need to fill in the `dadi-cli` subcommand in "Parameters". There is no easy way for users to upload frequency spectrum, as such `dadi-cli` can read https links that contain raw text data for the frequency spectrum, ex. https://tinyurl.com/u38zv4kw.
Users can also launch instances that run a work queue factory with or without `dadi-cli`, as such users can run one instance as a work queue factory and another instance running `dadi-cli` with work queue.

Users can access results via the Cacao deployment's Webshell or Webdesktop. If users provide a public ssh-key under [credentials](https://cacao.jetstream-cloud.org/credentials), they can also ssh into the instance with:
```
ssh USERNAME@PUBLIC_IP -i SSHKEY
```
Where `USERNAME` is the username for Cacao, `PUBLIC_IP` is the public IP of the deployment, and `SSHKEY` is the file that contains the private ssh-key information paired with the public key used for the deployment.
