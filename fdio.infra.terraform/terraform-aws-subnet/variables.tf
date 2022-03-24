variable "tags_name" {
  description = "Name used for tag."
  type        = string
  default     = ""
}

variable "tags_environment" {
  description = "Environment used for tag."
  type        = string
  default     = ""
}

# Variables for Subnet
variable "subnet_assign_ipv6_address_on_creation" {
  description = "Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address."
  type        = bool
  default     = false
}

variable "subnet_availability_zone" {
  description = "AZ for the subnet."
  type        = string
  default     = "us-east-1a"
}

variable "subnet_cidr_block" {
  description = "The IPv4 CIDR block for the subnet."
  type        = string
}

variable "subnet_ipv6_cidr_block" {
  description = "The IPv6 network range for the subnet, in CIDR notation."
  type        = string
}

variable "subnet_map_public_ip_on_launch" {
  description = "Specify true to indicate that instances launched into the subnet should be assigned a public IP address."
  type        = bool
  default     = false
}

variable "subnet_vpc_id" {
  description = "The VPC ID."
  type        = string
}
