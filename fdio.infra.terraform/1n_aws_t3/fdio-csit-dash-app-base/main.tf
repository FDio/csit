data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "elastic_beanstalk_application_version" {
  source                   = "../../terraform-aws-elastic-beanstalk-application-version"
  application_description  = "FD.io CSIT Results Dashboard"
  application_name         = "fdio-csit-dash-app"
  application_version_name = "fdio-csit-dash-app-base"
}
