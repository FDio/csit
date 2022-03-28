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

# Variables for elastic beanstalk VPC
variable "vpc_assign_generated_ipv6_cidr_block" {
  description = "Requests an Amazon-provided IPv6 CIDR block with a /56 prefix length for the VPC."
  type        = bool
  default     = true
}

variable "vpc_cidr_block" {
  description = "The CIDR block for the association."
  type        = string
  default     = "192.168.0.0/24"
}

variable "vpc_enable_dns_hostnames" {
  description = "Whether or not the VPC has DNS hostname support."
  type        = bool
  default     = true
}

variable "vpc_enable_dns_support" {
  description = "Whether or not the VPC has DNS support."
  type        = bool
  default     = true
}

variable "vpc_instance_tenancy" {
  description = "The allowed tenancy of instances launched into the selected VPC."
  type        = string
  default     = "default"
}

# Variables for Security Group
variable "security_group_description" {
  description = "Security group description."
  type        = string
  default     = "Allow inbound/outbound traffic"
}

variable "security_group_name" {
  description = "Name of the security group."
  type        = string
}

variable "security_group_revoke_rules_on_delete" {
  description = "Instruct Terraform to revoke all of the Security Groups attached ingress and egress rules before deleting the rule itself."
  type        = bool
  default     = false
}

variable "security_group_ingress" {
  description = "Ingress security group map."
  type        = list(any)
  default = [
    {
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      self             = false
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    },
    {
      from_port        = 0
      to_port          = 0
      protocol         = -1
      self             = true
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    },
  ]
}

variable "security_group_egress" {
  description = "Egress security group map."
  type        = list(any)
  default = [
    {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    },
  ]
}

# Variables for elastic beanstalk Subnet
variable "subnet_assign_ipv6_address_on_creation" {
  description = "Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address."
  type        = bool
  default     = false
}

variable "subnet_availability_zone" {
  description = "AWS availability zone"
  type        = string
  default     = "us-east-1a"
}

variable "subnet_map_public_ip_on_launch" {
  description = "Specify true to indicate that instances launched into the subnet should be assigned a public IP address."
  type        = bool
  default     = false
}
