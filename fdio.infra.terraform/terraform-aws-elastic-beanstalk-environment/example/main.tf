module "elastic_beanstalk_application" {
  source                  = "../../terraform-aws-elastic-beanstalk-application"
  application_description = "FD.io CSIT Results Dashboard"
  application_name        = "fdio-csit-dash-app"
}

module "elastic_beanstalk_environment" {
  source                  = "../"
  environment_application = module.elastic_beanstalk_application.application_name
  environment_description = module.elastic_beanstalk_application.application_description
  environment_name        = "fdio-csit-dash-env"
}
