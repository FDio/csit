module "vpc" {
  source                   = "../"
  security_group_name      = "terraform-sg"
  subnet_availability_zone = "us-east-1a"
  tags_name                = "terraform-vpc"
  tags_environment         = "terraform-vpc-environment"
}
