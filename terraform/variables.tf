
variable "instance_type" {
  description = "The type of AWS EC2 instance to deploy"
  default = "t3.xlarge"
}

variable "region" {
  description = "The region Terraform deploys your instance"
  default = "us-east-2"
}

