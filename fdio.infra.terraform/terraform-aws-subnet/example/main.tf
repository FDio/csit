module "vpc" {
  source                   = "../../terraform-aws-vpc"
  security_group_name      = "terraform-sg"
  subnet_availability_zone = "us-east-1a"
  tags_name                = "terraform-vpc"
  tags_environment         = "terraform-vpc-environment"
}

module "subnet" {
  source                   = "../"
  subnet_cidr_block        = "192.168.10.0/24"
  subnet_ipv6_cidr_block   = cidrsubnet(module.vpc.vpc_ipv6_cidr_block, 8, 1)
  subnet_availability_zone = "us-east-1a"
  tags_name                = "terraform-subnet"
  tags_environment         = "terraform-subnet-environment"
  subnet_vpc_id            = module.vpc.vpc_id
}
