ephemeral "vault_kv_secret_v2" "csit_docs" {
  mount = "kv"
  name  = "etl/csit_docs"
}

resource "aws_ssm_parameter" "csit_docs_access_key" {
  name             = "/fdio-csit-dash-app-m8g/AWS_ACCESS_KEY_ID"
  type             = "SecureString"
  value_wo         = ephemeral.vault_kv_secret_v2.csit_docs.data["access_key"]
  value_wo_version = 1
}

resource "aws_ssm_parameter" "csit_docs_secret_key" {
  name             = "/fdio-csit-dash-app-m8g/AWS_SECRET_ACCESS_KEY"
  type             = "SecureString"
  value_wo         = ephemeral.vault_kv_secret_v2.csit_docs.data["secret_key"]
  value_wo_version = 1
}

resource "aws_iam_role_policy" "read_app_secrets" {
  name = "fdio-csit-dash-app-m8g-read-secrets"
  role = "fdio-csit-dash-app-m8g-eb-ec2"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters"]
      Resource = [
        aws_ssm_parameter.csit_docs_access_key.arn,
        aws_ssm_parameter.csit_docs_secret_key.arn,
      ]
    }]
  })
  depends_on = [module.elastic_beanstalk_environment]
}

module "elastic_beanstalk_application" {
  providers = {
    aws = aws.deploy
  }

  source  = "pmikus/elastic-beanstalk-application/aws"
  version = "1.0.0"

  # application
  application_description                    = "FD.io CDASH M8G"
  application_name                           = "fdio-csit-dash-app-m8g"
  appversion_lifecycle_service_role_arn      = "arn:aws:iam::407116685360:role/aws-service-role/elasticbeanstalk.amazonaws.com/AWSServiceRoleForElasticBeanstalk"
  appversion_lifecycle_max_count             = 10
  appversion_lifecycle_delete_source_from_s3 = false
}

module "elastic_beanstalk_environment" {
  providers = {
    aws = aws.deploy
  }

  source  = "pmikus/elastic-beanstalk-environment/aws"
  version = "1.0.3"

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
  environment_solution_stack_name    = "64bit Amazon Linux 2023 v4.14.4 running Python 3.15"
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
    "AWS_DEFAULT_REGION" = "us-east-1"
  }
  environment_secrets = {
    "AWS_ACCESS_KEY_ID"     = aws_ssm_parameter.csit_docs_access_key.arn
    "AWS_SECRET_ACCESS_KEY" = aws_ssm_parameter.csit_docs_secret_key.arn
  }
  #environment_variables = {
  #  "AWS_ACCESS_KEY_ID"     = ephemeral.vault_kv_secret_v2.csit_docs.data["access_key"]
  #  "AWS_SECRET_ACCESS_KEY" = ephemeral.vault_kv_secret_v2.csit_docs.data["secret_key"]
  #  "AWS_DEFAULT_REGION"    = ephemeral.vault_kv_secret_v2.csit_docs.data["region"]
  #}
}
