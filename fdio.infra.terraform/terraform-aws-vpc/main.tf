locals {
  tags = {
    "Name"        = "${var.tags_name}"
    "Environment" = "${var.tags_environment}"
  }
}

# Create VPC
resource "aws_vpc" "vpc" {
  assign_generated_ipv6_cidr_block = var.vpc_assign_generated_ipv6_cidr_block
  cidr_block                       = var.vpc_cidr_block
  enable_dns_hostnames             = var.vpc_enable_dns_hostnames
  enable_dns_support               = var.vpc_enable_dns_support
  instance_tenancy                 = var.vpc_instance_tenancy
  tags                             = local.tags
}

# Create Security Group
resource "aws_security_group" "security_group" {
  depends_on = [
    aws_vpc.vpc
  ]
  description            = var.security_group_description
  name                   = var.security_group_name
  revoke_rules_on_delete = var.security_group_revoke_rules_on_delete
  tags                   = local.tags
  vpc_id                 = aws_vpc.vpc.id

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = 0
    to_port          = 0
    protocol         = -1
    self             = true
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    ipv6_cidr_blocks = ["::/0"]
  }
}

# Create Internet Gateway
resource "aws_internet_gateway" "internet_gateway" {
  depends_on = [
    aws_vpc.vpc
  ]
  tags   = local.tags
  vpc_id = aws_vpc.vpc.id
}

# Create Route
resource "aws_route" "route" {
  depends_on = [
    aws_vpc.vpc,
    aws_internet_gateway.internet_gateway
  ]
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.internet_gateway.id
  route_table_id         = aws_vpc.vpc.main_route_table_id
}

# Create Subnet
resource "aws_subnet" "subnet" {
  depends_on = [
    aws_vpc.vpc
  ]
  assign_ipv6_address_on_creation = var.subnet_assign_ipv6_address_on_creation
  availability_zone               = var.subnet_availability_zone
  cidr_block                      = aws_vpc.vpc.cidr_block
  ipv6_cidr_block                 = cidrsubnet(aws_vpc.vpc.ipv6_cidr_block, 8, 1)
  map_public_ip_on_launch         = var.subnet_map_public_ip_on_launch
  tags                            = local.tags
  vpc_id                          = aws_vpc.vpc.id
}
