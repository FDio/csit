<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.4 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.3.0 |
| <a name="requirement_vault"></a> [vault](#requirement\_vault) | >= 3.2.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 4.3.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_elastic_beanstalk_environment.environment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elastic_beanstalk_environment) | resource |
| [aws_iam_instance_profile.ec2_iam_instance_profile](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_instance_profile) | resource |
| [aws_iam_role.ec2](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.service](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.ecr_readonly](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.enhanced_health](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.multicontainer_docker](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.service](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ssm_automation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.ssm_ec2](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.web_tier](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.worker_tier](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_internet_gateway.internet_gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway) | resource |
| [aws_route.route](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route) | resource |
| [aws_ssm_activation.ec2](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_activation) | resource |
| [aws_subnet.subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_vpc.vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc) | resource |
| [aws_iam_policy_document.default](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.ec2](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.service](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_application_description"></a> [application\_description](#input\_application\_description) | Short description of the application. | `string` | `"Beanstalk Application"` | no |
| <a name="input_application_name"></a> [application\_name](#input\_application\_name) | The name of the application, must be unique within account. | `string` | `"Beanstalk"` | no |
| <a name="input_appversion_lifecycle_delete_source_from_s3"></a> [appversion\_lifecycle\_delete\_source\_from\_s3](#input\_appversion\_lifecycle\_delete\_source\_from\_s3) | Whether to delete application versions from S3 source | `bool` | `false` | no |
| <a name="input_appversion_lifecycle_max_count"></a> [appversion\_lifecycle\_max\_count](#input\_appversion\_lifecycle\_max\_count) | The max number of application versions to keep | `number` | `2` | no |
| <a name="input_appversion_lifecycle_service_role_arn"></a> [appversion\_lifecycle\_service\_role\_arn](#input\_appversion\_lifecycle\_service\_role\_arn) | The service role ARN to use for application version cleanup. If left empty, the `appversion_lifecycle` block will not be created. | `string` | `""` | no |
| <a name="input_associate_public_ip_address"></a> [associate\_public\_ip\_address](#input\_associate\_public\_ip\_address) | Whether to associate public IP addresses to the instances. | `bool` | `true` | no |
| <a name="input_autoscaling_asg_maxsize"></a> [autoscaling\_asg\_maxsize](#input\_autoscaling\_asg\_maxsize) | Maximum instances to launch | `number` | `2` | no |
| <a name="input_autoscaling_asg_minsize"></a> [autoscaling\_asg\_minsize](#input\_autoscaling\_asg\_minsize) | Minumum instances to launch | `number` | `1` | no |
| <a name="input_autoscaling_trigger_lower_breach_scale_increment"></a> [autoscaling\_trigger\_lower\_breach\_scale\_increment](#input\_autoscaling\_trigger\_lower\_breach\_scale\_increment) | How many Amazon EC2 instances to remove when performing a scaling activity. | `number` | `-1` | no |
| <a name="input_autoscaling_trigger_lower_threshold"></a> [autoscaling\_trigger\_lower\_threshold](#input\_autoscaling\_trigger\_lower\_threshold) | Minimum level of autoscale metric to remove an instance | `number` | `20` | no |
| <a name="input_autoscaling_trigger_measure_name"></a> [autoscaling\_trigger\_measure\_name](#input\_autoscaling\_trigger\_measure\_name) | Metric used for your Auto Scaling trigger | `string` | `"CPUUtilization"` | no |
| <a name="input_autoscaling_trigger_statistic"></a> [autoscaling\_trigger\_statistic](#input\_autoscaling\_trigger\_statistic) | Statistic the trigger should use, such as Average | `string` | `"Average"` | no |
| <a name="input_autoscaling_trigger_unit"></a> [autoscaling\_trigger\_unit](#input\_autoscaling\_trigger\_unit) | Unit for the trigger measurement, such as Bytes | `string` | `"Percent"` | no |
| <a name="input_autoscaling_trigger_upper_breach_scale_increment"></a> [autoscaling\_trigger\_upper\_breach\_scale\_increment](#input\_autoscaling\_trigger\_upper\_breach\_scale\_increment) | How many Amazon EC2 instances to add when performing a scaling activity | `number` | `1` | no |
| <a name="input_autoscaling_trigger_upper_threshold"></a> [autoscaling\_trigger\_upper\_threshold](#input\_autoscaling\_trigger\_upper\_threshold) | Maximum level of autoscale metric to add an instance | `number` | `80` | no |
| <a name="input_cloudwatch_logs_delete_on_terminate"></a> [cloudwatch\_logs\_delete\_on\_terminate](#input\_cloudwatch\_logs\_delete\_on\_terminate) | Whether to delete the log groups when the environment is terminated. If false, the logs are kept RetentionInDays days | `bool` | `true` | no |
| <a name="input_cloudwatch_logs_health_delete_on_terminate"></a> [cloudwatch\_logs\_health\_delete\_on\_terminate](#input\_cloudwatch\_logs\_health\_delete\_on\_terminate) | Whether to delete the log group when the environment is terminated. If false, the health data is kept RetentionInDays days. | `bool` | `true` | no |
| <a name="input_cloudwatch_logs_health_health_streaming_enabled"></a> [cloudwatch\_logs\_health\_health\_streaming\_enabled](#input\_cloudwatch\_logs\_health\_health\_streaming\_enabled) | For environments with enhanced health reporting enabled, whether to create a group in CloudWatch Logs for environment health and archive Elastic Beanstalk environment health data. For information about enabling enhanced health, see aws:elasticbeanstalk:healthreporting:system. | `bool` | `true` | no |
| <a name="input_cloudwatch_logs_health_retention_in_days"></a> [cloudwatch\_logs\_health\_retention\_in\_days](#input\_cloudwatch\_logs\_health\_retention\_in\_days) | The number of days to keep the archived health data before it expires. | `number` | `3` | no |
| <a name="input_cloudwatch_logs_retention_in_days"></a> [cloudwatch\_logs\_retention\_in\_days](#input\_cloudwatch\_logs\_retention\_in\_days) | The number of days to keep log events before they expire. | `number` | `3` | no |
| <a name="input_cloudwatch_logs_stream_logs"></a> [cloudwatch\_logs\_stream\_logs](#input\_cloudwatch\_logs\_stream\_logs) | Whether to create groups in CloudWatch Logs for proxy and deployment logs, and stream logs from each instance in your environment | `bool` | `true` | no |
| <a name="input_default_listener_enabled"></a> [default\_listener\_enabled](#input\_default\_listener\_enabled) | Set to false to disable the listener. You can use this option to disable the default listener on port 80. | `bool` | `true` | no |
| <a name="input_elb_scheme"></a> [elb\_scheme](#input\_elb\_scheme) | Specify `internal` if you want to create an internal load balancer in your Amazon VPC so that your Elastic Beanstalk application cannot be accessed from outside your Amazon VPC. | `string` | `"public"` | no |
| <a name="input_environment_application"></a> [environment\_application](#input\_environment\_application) | The name of the application, must be unique within account. | `string` | `"Beanstalk Application"` | no |
| <a name="input_environment_description"></a> [environment\_description](#input\_environment\_description) | Short description of the environment. | `string` | `"Beanstalk Environment"` | no |
| <a name="input_environment_loadbalancer_type"></a> [environment\_loadbalancer\_type](#input\_environment\_loadbalancer\_type) | Load Balancer type, e.g. 'application' or 'classic'. | `string` | `"network"` | no |
| <a name="input_environment_name"></a> [environment\_name](#input\_environment\_name) | A unique name for this Environment. This name is used in the application URL. | `string` | `"Beanstalk-env"` | no |
| <a name="input_environment_process_default_healthcheck_interval"></a> [environment\_process\_default\_healthcheck\_interval](#input\_environment\_process\_default\_healthcheck\_interval) | The interval of time, in seconds, that Elastic Load Balancing checks the health of the Amazon EC2 instances of your application. | `number` | `10` | no |
| <a name="input_environment_process_default_healthy_threshold_count"></a> [environment\_process\_default\_healthy\_threshold\_count](#input\_environment\_process\_default\_healthy\_threshold\_count) | The number of consecutive successful requests before Elastic Load Balancing changes the instance health status. | `number` | `3` | no |
| <a name="input_environment_process_default_port"></a> [environment\_process\_default\_port](#input\_environment\_process\_default\_port) | Port application is listening on. | `number` | `5000` | no |
| <a name="input_environment_process_default_unhealthy_threshold_count"></a> [environment\_process\_default\_unhealthy\_threshold\_count](#input\_environment\_process\_default\_unhealthy\_threshold\_count) | The number of consecutive unsuccessful requests before Elastic Load Balancing changes the instance health status. | `number` | `3` | no |
| <a name="input_environment_solution_stack_name"></a> [environment\_solution\_stack\_name](#input\_environment\_solution\_stack\_name) | A solution stack to base your environment off of. | `string` | `"64bit Amazon Linux 2 v3.3.11 running Python 3.8"` | no |
| <a name="input_environment_tier"></a> [environment\_tier](#input\_environment\_tier) | The environment tier specified. | `string` | `"WebServer"` | no |
| <a name="input_environment_type"></a> [environment\_type](#input\_environment\_type) | Environment type, e.g. 'LoadBalanced' or 'SingleInstance'. If setting to 'SingleInstance', `rolling_update_type` must be set to 'Time', `updating_min_in_service` must be set to 0, and `loadbalancer_subnets` will be unused (it applies to the ELB, which does not exist in SingleInstance environments). | `string` | `"LoadBalanced"` | no |
| <a name="input_environment_variables"></a> [environment\_variables](#input\_environment\_variables) | Map of custom ENV variables to be provided to the application. | `map(string)` | `{}` | no |
| <a name="input_environment_version_label"></a> [environment\_version\_label](#input\_environment\_version\_label) | The name of the Elastic Beanstalk Application Version to use in deployment. | `string` | `""` | no |
| <a name="input_environment_wait_for_ready_timeout"></a> [environment\_wait\_for\_ready\_timeout](#input\_environment\_wait\_for\_ready\_timeout) | The maximum duration to wait for the Elastic Beanstalk Environment to be in a ready state before timing out | `string` | `"20m"` | no |
| <a name="input_healthreporting_system_type"></a> [healthreporting\_system\_type](#input\_healthreporting\_system\_type) | Whether to enable enhanced health reporting for this environment | `string` | `"enhanced"` | no |
| <a name="input_hostmanager_log_publication_control"></a> [hostmanager\_log\_publication\_control](#input\_hostmanager\_log\_publication\_control) | Copy the log files for your application's Amazon EC2 instances to the Amazon S3 bucket associated with your application | `bool` | `true` | no |
| <a name="input_instances_instance_types"></a> [instances\_instance\_types](#input\_instances\_instance\_types) | Instances type | `string` | `"t3.medium"` | no |
| <a name="input_managedactions_managed_actions_enabled"></a> [managedactions\_managed\_actions\_enabled](#input\_managedactions\_managed\_actions\_enabled) | Enable managed platform updates. When you set this to true, you must also specify a `PreferredStartTime` and `UpdateLevel` | `bool` | `true` | no |
| <a name="input_managedactions_platformupdate_instance_refresh_enabled"></a> [managedactions\_platformupdate\_instance\_refresh\_enabled](#input\_managedactions\_platformupdate\_instance\_refresh\_enabled) | Enable weekly instance replacement. | `bool` | `true` | no |
| <a name="input_managedactions_platformupdate_update_level"></a> [managedactions\_platformupdate\_update\_level](#input\_managedactions\_platformupdate\_update\_level) | The highest level of update to apply with managed platform updates | `string` | `"minor"` | no |
| <a name="input_managedactions_preferred_start_time"></a> [managedactions\_preferred\_start\_time](#input\_managedactions\_preferred\_start\_time) | Configure a maintenance window for managed actions in UTC | `string` | `"Sun:10:00"` | no |
| <a name="input_subnet_availability_zone"></a> [subnet\_availability\_zone](#input\_subnet\_availability\_zone) | AWS availability zone | `string` | `"us-east-1a"` | no |
| <a name="input_vpc_cidr_block"></a> [vpc\_cidr\_block](#input\_vpc\_cidr\_block) | The CIDR block for the association. | `string` | `"192.168.0.0/24"` | no |
| <a name="input_vpc_enable_dns_hostnames"></a> [vpc\_enable\_dns\_hostnames](#input\_vpc\_enable\_dns\_hostnames) | Whether or not the VPC has DNS hostname support. | `bool` | `true` | no |
| <a name="input_vpc_enable_dns_support"></a> [vpc\_enable\_dns\_support](#input\_vpc\_enable\_dns\_support) | Whether or not the VPC has DNS support. | `bool` | `true` | no |
| <a name="input_vpc_instance_tenancy"></a> [vpc\_instance\_tenancy](#input\_vpc\_instance\_tenancy) | The allowed tenancy of instances launched into the selected VPC. | `string` | `"default"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_environment_cname"></a> [environment\_cname](#output\_environment\_cname) | n/a |
| <a name="output_environment_name"></a> [environment\_name](#output\_environment\_name) | n/a |
<!-- END_TF_DOCS -->