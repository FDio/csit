variable "region" {
  description = "AWS Region"
  type = string
  default = "eu-central-1"
}

variable "avail_zone" {
  description = "AWS availability zone"
  type = string
  default = "eu-central-1a"
}

variable "ami_image" {
  # eu-central-1/focal-20.04-amd64-hvm-ssd-20210119.1
  # kernel 5.4.0-1035-aws (~5.4.0-65)
  description = "AWS AMI image ID"
  type = string
  default = "ami-0a875db8a031a9efb"
}

variable "instance_type" {
  description = "AWS instance type"
  type = string
  default = "c5n.4xlarge"
}

variable "testbed_name" {
  description = "Testbed name"
  type = string
  default = "testbed1"
}
