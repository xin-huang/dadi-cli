terraform {
  required_version = ">= 0.13"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}


provider "aws" {
  region = var.AWS.region
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*20*-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_vpc" "vpc" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_subnet" "subnet_public" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = "10.1.0.0/24"
}

resource "aws_route_table" "rtb_public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "rta_subnet_public" {
  subnet_id      = aws_subnet.subnet_public.id
  route_table_id = aws_route_table.rtb_public.id
}

resource "aws_security_group" "sg_22_9123" {
  name   = "sg_dadi"
  vpc_id = aws_vpc.vpc.id

  # SSH access from the VPC
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 9123
    to_port     = 9123
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


  ingress {
    from_port   = 9123
    to_port     = 9123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  template_vars = {
    dadi_cli = var.dadi_cli
    project_name = "${var.project_name}"
    public_key = "${var.AWS.public_key}"
    workqueue_factory = var.workqueue_factory
    workqueue_password = "${var.workqueue_password}"
  }
}

resource "aws_instance" "dadi_manager" {
  count = var.dadi_cli.run ? 1 : 0
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.AWS.instance_type
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_22_9123.id]
  associate_public_ip_address = true
  user_data                   = templatefile("dadi.tftpl", local.template_vars)

  root_block_device {
    volume_type = "gp2"
    volume_size = "16"
  }

  tags = {
    Name = "Dadi"
  }
  provisioner "file" {
    source = "uploads/"
    destination = "/home/dadi"
    connection {
      type        = "ssh"
      user        = "dadi"
      private_key = "${file("ssh-key")}"
      host        = "${self.public_dns}"
    }
  }
}
resource "aws_instance" "dadi" {
  count = var.dadi_cli.run ? 0 : 1
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.AWS.instance_type
  subnet_id                   = aws_subnet.subnet_public.id
  vpc_security_group_ids      = [aws_security_group.sg_22_9123.id]
  associate_public_ip_address = true
  user_data                   = templatefile("dadi.tftpl", local.template_vars)

  root_block_device {
    volume_type = "gp2"
    volume_size = "16"
  }

  tags = {
    Name = "Dadi"
  }
}

output "public_ip" {
  value = var.dadi_cli.run ? aws_instance.dadi_manager[0].public_ip : aws_instance.dadi[0].public_ip
}
