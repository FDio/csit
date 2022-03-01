output "cname" {
  value = aws_elastic_beanstalk_environment.elasticenv.cname
}

output "envName" {
  value = aws_elastic_beanstalk_environment.elasticenv.name
}

output "asgName" {
  value = aws_elastic_beanstalk_environment.elasticenv.autoscaling_groups[0]
}

output "lbarn" {
  value = aws_elastic_beanstalk_environment.elasticenv.load_balancers[0]
}