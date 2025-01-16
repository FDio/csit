data "vault_kv_secret_v2" "fdio_docs" {
  mount = "kv"
  name  = "etl/fdio_docs"
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "elastic_beanstalk_application" {
  source = "../terraform-aws-elastic-beanstalk-application"

  # application
  application_description                    = "FD.io CDASH M8G"
  application_name                           = "fdio-csit-dash-app-m8g"
  appversion_lifecycle_service_role_arn      = "arn:aws:iam::407116685360:role/aws-service-role/elasticbeanstalk.amazonaws.com/AWSServiceRoleForElasticBeanstalk"
  appversion_lifecycle_max_count             = 10
  appversion_lifecycle_delete_source_from_s3 = false
}

module "elastic_beanstalk_environment" {
  source = "../terraform-aws-elastic-beanstalk-environment"

  # environment
  application_name = "fdio-csit-dash-app-m8g"

  # vpc
  vpc_cidr_block           = "10.0.0.0/16"
  vpc_enable_dns_hostnames = true
  vpc_enable_dns_support   = true
  vpc_instance_tenancy     = "default"

  # subnet
  subnet_a_availability_zone = "us-east-1a"
  subnet_a_cidr_block        = "10.0.0.0/20"
  subnet_b_availability_zone = "us-east-1b"
  subnet_b_cidr_block        = "10.0.16.0/20"

  # environment
  environment_application            = module.elastic_beanstalk_application.application_name
  environment_description            = module.elastic_beanstalk_application.application_description
  environment_name                   = "fdio-csit-dash-env-m8g"
  environment_solution_stack_name    = "64bit Amazon Linux 2023 v4.3.2 running Python 3.12"
  environment_tier                   = "WebServer"
  environment_wait_for_ready_timeout = "25m"
  environment_version_label          = ""

  # aws:ec2:instances
  instances_instance_types = "m8g.2xlarge"

  # aws:ec2:vpc
  associate_public_ip_address = true
  elb_scheme                  = "public"

  # aws:elbv2:listener:default
  default_listener_enabled = true

  # aws:elasticbeanstalk:environment
  environment_loadbalancer_type               = "application"
  environment_loadbalancer_ssl_certificate_id = "arn:aws:acm:us-east-1:407116685360:certificate/3439b8aa-4f07-496f-a2de-e38159050c85"

  # aws:elasticbeanstalk:environment:process:default
  environment_process_default_healthcheck_interval      = 10
  environment_process_default_healthy_threshold_count   = 3
  environment_process_default_port                      = 5000
  environment_process_default_unhealthy_threshold_count = 3

  # aws:autoscaling:updatepolicy:rollingupdate
  autoscaling_updatepolicy_rolling_update_enabled  = true
  autoscaling_updatepolicy_rolling_update_type     = "Immutable"
  autoscaling_updatepolicy_min_instance_in_service = 1

  # aws:elasticbeanstalk:command
  command_deployment_policy = "Rolling"

  # aws:autoscaling:updatepolicy:rollingupdate
  updatepolicy_max_batch_size = 1

  # aws:elasticbeanstalk:healthreporting:system
  healthreporting_system_type = "enhanced"

  # aws:elasticbeanstalk:managedactions
  managedactions_managed_actions_enabled = true
  managedactions_preferred_start_time    = "Sun:10:00"

  # aws:elasticbeanstalk:managedactions:platformupdate
  managedactions_platformupdate_update_level             = "minor"
  managedactions_platformupdate_instance_refresh_enabled = true

  # aws:autoscaling:asg
  autoscaling_asg_minsize = 1
  autoscaling_asg_maxsize = 2

  # aws:autoscaling:trigger
  autoscaling_trigger_measure_name                 = "CPUUtilization"
  autoscaling_trigger_statistic                    = "Average"
  autoscaling_trigger_unit                         = "Percent"
  autoscaling_trigger_lower_threshold              = 20
  autoscaling_trigger_lower_breach_scale_increment = -1
  autoscaling_trigger_upper_threshold              = 80
  autoscaling_trigger_upper_breach_scale_increment = 1

  # aws:elasticbeanstalk:hostmanager
  hostmanager_log_publication_control = true

  # aws:elasticbeanstalk:cloudwatch:logs
  cloudwatch_logs_stream_logs         = true
  cloudwatch_logs_delete_on_terminate = true
  cloudwatch_logs_retention_in_days   = 3

  # aws:elasticbeanstalk:cloudwatch:logs:health
  cloudwatch_logs_health_health_streaming_enabled = true
  cloudwatch_logs_health_delete_on_terminate      = true
  cloudwatch_logs_health_retention_in_days        = 3

  environment_type = "LoadBalanced"

  # aws:elasticbeanstalk:application:environment
  environment_variables = {
    "AWS_ACCESS_KEY_ID"     = data.vault_kv_secret_v2.fdio_docs.data["access_key"]
    "AWS_SECRET_ACCESS_KEY" = data.vault_kv_secret_v2.fdio_docs.data["secret_key"]
    "AWS_DEFAULT_REGION"    = data.vault_kv_secret_v2.fdio_docs.data["region"]
  }
}
