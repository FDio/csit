variable "region" {
  description = "AWS Region."
  type        = string
  default     = "eu-central-1"
}

variable "resources_name_prefix" {
  description = "Resources name prefix."
  type        = string
  default     = "csit_2n_aws_c5n"
}

variable "testbed_name" {
  description = "Testbed name."
  type        = string
  default     = "testbed1"
}

# Variables for Private Key
variable "private_key_algorithm" {
  description = "The name of the algorithm to use for the key."
  type        = string
  default     = "RSA"
}

variable "private_key_ecdsa_curve" {
  description = "When algorithm is ECDSA, the name of the elliptic curve to use."
  type        = string
  default     = "P521"
}

variable "private_key_rsa_bits" {
  description = "When algorithm is RSA, the size of the generated RSA key in bits."
  type        = number
  default     = 4096
}

# Variables for Placement Group
variable "placement_group_strategy" {
  description = "The placement strategy. Can be cluster, partition or spread."
  type        = string
  default     = "cluster"
}

# Variables for Instance