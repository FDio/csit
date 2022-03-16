output "elastic_beanstalk_application_name" {
  value       = module.elastic_beanstalk_application.application_name
  description = "Elastic Beanstalk Application name"
}

output "elastic_beanstalk_application_description" {
  value       = module.elastic_beanstalk_application.application_description
  description = "Elastic Beanstalk Application description"
}
