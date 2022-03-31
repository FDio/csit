module "fdio-logs" {
  # fdio logs iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-logs"
}

module "fdio-docs" {
  # fdio docs iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-docs"
}

module "fdio-csit-jenkins" {
  # fdio csit jenkins iam
  source = "../"
  name   = "dynamic-aws-creds-vault-fdio-csit-jenkins"
}
