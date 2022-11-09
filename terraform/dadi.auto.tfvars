
AWS = {
  # the type of AWS instance to create (required)
  instance_type = "t2.xlarge"

  # AWS region for the instance (required)
  region = "us-east-1"

  # the public part of your SSH key, used for connecting to the instance (required)
  public_key = ""
}

dadi_cli = {
  # set to true to run dadi-cli automatically
  run = false

  # set to the parameters you want for dadi-cli, don't include the --fs and --work-queue parameters, they will be added using the values from this file
  # example: "InferDM --model two_epoch --p0 1 1 --ubounds 10 10 --lbounds 10e-3 10e-3 --grids 30 40 50 --output aws.two_epoch.demo.params --optimizations 2 --nomisid"
  parameters = ""
}

workqueue_factory = {
  # set to true to run workqueue_factory automatically
  run = false
}

# value for project name parameter (required if either dadi-cli or workqueue_factory is set to run)
project_name = ""

# value for workqueue password parameter (required if either dadi-cli or workqueue_factory is set to run)
workqueue_password = ""
