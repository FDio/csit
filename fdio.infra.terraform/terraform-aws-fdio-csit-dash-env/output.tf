output "elastic_beanstalk_environment_hostname" {
  description = "DNS hostname"
  value       = module.elastic_beanstalk_environment.environment_cname
}
