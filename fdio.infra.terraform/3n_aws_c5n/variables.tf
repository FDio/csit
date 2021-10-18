variable "region" {
  description = "AWS Region"
  type        = string
  default     = "eu-central-1"
}

variable "vault-name" {
  default = "dynamic-aws-creds-vault-admin"
}

variable "avail_zone" {
  description = "AWS availability zone"
  type        = string
  default     = "eu-central-1c"
}

variable "ami_image_tg" {
  # eu-central-1/focal-20.04-amd64-hvm-ssd-20210119.1
  # kernel 5.4.0-1035-aws (~5.4.0-65)
  description = "AWS AMI image ID"
  type        = string
  default     = "ami-0d6bc0344dc036b9d"
}

variable "ami_image_sut" {
  # eu-central-1/focal-20.04-amd64-hvm-ssd-20210119.1
  # kernel 5.4.0-1035-aws (~5.4.0-65)
  description = "AWS AMI image ID"
  type        = string
  default     = "ami-012c9c631964367be"
}

variable "instance_initiated_shutdown_behavior" {
  description = "Shutdown behavior for the instance"
  type        = string
  default     = "terminate"
}

variable "instance_type" {
  description = "AWS instance type"
  type        = string
  default     = "c5n.9xlarge"
}

variable "testbed_name" {
  description = "Testbed name"
  type        = string
  default     = "testbed1"
}

variable "topology_name" {
  description = "Topology name"
  type        = string
  default     = "3n_aws_c5n"
}

variable "environment_name" {
  description = "Environment name"
  type        = string
  default     = "CSIT-AWS"
}

variable "resources_name_prefix" {
  description = "Resources name prefix"
  type        = string
  default     = "CSIT_3n_aws_c5n"
}
