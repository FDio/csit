locals {
  tags = {
    "Name"        = "${var.tags_name}"
    "Environment" = "${var.tags_environment}"
  }
}

# Create VPC IPv4 CIDR Block Association
resource "aws_vpc_ipv4_cidr_block_association" "ipv4_cidr_block_association" {
  cidr_block = var.cidr_block
  vpc_id     = var.vpc_id
}

# Create Subnet
resource "aws_subnet" "subnet" {
  depends_on = [
    aws_vpc_ipv4_cidr_block_association.ipv4_cidr_block_association
  ]
  assign_ipv6_address_on_creation = var.assign_ipv6_address_on_creation
  availability_zone               = var.availability_zone
  cidr_block                      = var.cidr_block
  ipv6_cidr_block                 = var.ipv6_cidr_block
  map_public_ip_on_launch         = var.subnet_map_public_ip_on_launch
  tags                            = local.tags
  vpc_id                          = var.vpc_id
}
