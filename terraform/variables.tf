
variable "instance_type" {
  description = "The type of AWS EC2 instance to deploy"
  default = "t3.xlarge"
}

variable "region" {
  description = "The region Terraform deploys your instance"
  default = "us-east-1"
}

variable "public_key" {
  description = "The contents of your public key file for connecting to the isntance"
  default = ""
}

variable "project_name" {
  description = "Optional name for project, if set workqueue_factory will be run automatically"
  default = ""
}

variable "workqueue_password" {
  description = "Optional password to be used by Work Queue"
  default = ""
}
