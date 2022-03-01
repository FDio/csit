output "cname" {
  value = aws_elastic_beanstalk_environment.environment.cname
}

output "envName" {
  value = aws_elastic_beanstalk_environment.environment.name
}

output "asgName" {
  value = aws_elastic_beanstalk_environment.environment.autoscaling_groups[0]
}

output "lbarn" {
  value = aws_elastic_beanstalk_environment.environment.load_balancers[0]
}