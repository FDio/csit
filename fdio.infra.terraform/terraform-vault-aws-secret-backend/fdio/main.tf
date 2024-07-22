module "fdio-logs" {
  # fdio logs iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-logs"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
}

module "fdio-docs" {
  # fdio docs iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-docs"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
}

module "fdio-csit-jenkins" {
  # fdio csit jenkins iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-csit-jenkins"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
}
