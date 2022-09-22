
variable "instance_type" {
  description = "The type of AWS EC2 instance to deploy"
  default = "t3.xlarge"
}

variable "region" {
  description = "The region Terraform deploys your instance"
  default = "us-east-2"
}

variable "workqueue_password" {
  description = "Optional password to be used by Work Queue"
  default = ""
}
