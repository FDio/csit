# Variables for elastic beanstalk VPC
variable "vpc_cidr_block" {
  description = "The CIDR block for the association."
  type        = string
  default     = "192.168.0.0/24"
}

variable "vpc_enable_dns_hostnames" {
  description = "Whether or not the VPC has DNS hostname support."
  type        = bool
  default     = true
}

variable "vpc_enable_dns_support" {
  description = "Whether or not the VPC has DNS support."
  type        = bool
  default     = true
}

variable "vpc_instance_tenancy" {
  description = "The allowed tenancy of instances launched into the selected VPC."
  type        = string
  default     = "default"
}

# Variables for elastic beanstalk Subnet
variable "subnet_availability_zone" {
  description = "AWS availability zone"
  type        = string
  default     = "us-east-1a"
}

# Variables for elastic beanstalk Application
variable "environment_application" {
  description = "The name of the application, must be unique within account."
  type        = string
  default     = "Beanstalk Application"
}

variable "application_description" {
  description = "Short description of the application."
  type        = string
  default     = "Beanstalk Application"
}

variable "application_name" {
  description = "The name of the application, must be unique within account."
  type        = string
  default     = "Beanstalk"
}

variable "appversion_lifecycle_service_role_arn" {
  description = "The service role ARN to use for application version cleanup. If left empty, the `appversion_lifecycle` block will not be created."
  type        = string
  default     = ""
}

variable "appversion_lifecycle_max_count" {
  description = "The max number of application versions to keep"
  type        = number
  default     = 2
}

variable "appversion_lifecycle_delete_source_from_s3" {
  description = "Whether to delete application versions from S3 source"
  type        = bool
  default     = false
}

# Variables for elastic beanstalk Environment
variable "environment_description" {
  description = "Short description of the environment."
  type        = string
  default     = "Beanstalk Environment"
}

variable "environment_name" {
  description = "A unique name for this Environment. This name is used in the application URL."
  type        = string
  default     = "Beanstalk-env"
}

variable "environment_solution_stack_name" {
  description = "A solution stack to base your environment off of."
  type        = string
  default     = "64bit Amazon Linux 2 v3.3.11 running Python 3.8"
}

variable "environment_tier" {
  description = "The environment tier specified."
  type        = string
  default     = "WebServer"
}

variable "environment_wait_for_ready_timeout" {
  description = "The maximum duration to wait for the Elastic Beanstalk Environment to be in a ready state before timing out"
  type        = string
  default     = "20m"
}

variable "environment_version_label" {
  description = "The name of the Elastic Beanstalk Application Version to use in deployment."
  type        = string
  default     = ""
}

# aws:ec2:instances
variable "instances_instance_types" {
  description = "Instances type"
  type        = string
  default     = "t3.medium"
}

# aws:ec2:vpc
variable "associate_public_ip_address" {
  description = "Whether to associate public IP addresses to the instances."
  type        = bool
  default     = true
}

variable "elb_scheme" {
  description = "Specify `internal` if you want to create an internal load balancer in your Amazon VPC so that your Elastic Beanstalk application cannot be accessed from outside your Amazon VPC."
  type        = string
  default     = "public"
}

# aws:elbv2:listener:default
variable "default_listener_enabled" {
  description = "Set to false to disable the listener. You can use this option to disable the default listener on port 80."
  type        = bool
  default     = true
}

# aws:elasticbeanstalk:environment
variable "environment_loadbalancer_type" {
  description = "Load Balancer type, e.g. 'application' or 'classic'."
  type        = string
  default     = "network"
}

# aws:elasticbeanstalk:environment:process:default
variable "environment_process_default_healthcheck_interval" {
  description = "The interval of time, in seconds, that Elastic Load Balancing checks the health of the Amazon EC2 instances of your application."
  type        = number
  default     = 10
}

variable "environment_process_default_healthy_threshold_count" {
  description = "The number of consecutive successful requests before Elastic Load Balancing changes the instance health status."
  type        = number
  default     = 3
}

variable "environment_process_default_port" {
  description = "Port application is listening on."
  type        = number
  default     = 5000
}

variable "environment_process_default_unhealthy_threshold_count" {
  description = "The number of consecutive unsuccessful requests before Elastic Load Balancing changes the instance health status."
  type        = number
  default     = 3
}

# aws:autoscaling:updatepolicy:rollingupdate
variable "autoscaling_updatepolicy_rolling_update_enabled" {
  description = "Whether to enable rolling update."
  type        = bool
  default     = true
}

variable "autoscaling_updatepolicy_rolling_update_type" {
  description = "`Health` or `Immutable`. Set it to `Immutable` to apply the configuration change to a fresh group of instances."
  type        = string
  default     = "Immutable"
}

variable "autoscaling_updatepolicy_min_instance_in_service" {
  description = "Minimum number of instances in service during update."
  type        = number
  default     = 1
}

# aws:elasticbeanstalk:command
variable "command_deployment_policy" {
  description = "Use the DeploymentPolicy option to set the deployment type. The following values are supported: `AllAtOnce`, `Rolling`, `RollingWithAdditionalBatch`, `Immutable`, `TrafficSplitting`."
  type        = string
  default     = "Rolling"
}

# aws:autoscaling:updatepolicy:rollingupdate
variable "updatepolicy_max_batch_size" {
  description = "Maximum number of instances to update at once."
  type        = number
  default     = 1
}

# aws:elasticbeanstalk:healthreporting:system
variable "healthreporting_system_type" {
  description = "Whether to enable enhanced health reporting for this environment"
  type        = string
  default     = "enhanced"
}

# aws:elasticbeanstalk:managedactions
variable "managedactions_managed_actions_enabled" {
  description = "Enable managed platform updates. When you set this to true, you must also specify a `PreferredStartTime` and `UpdateLevel`"
  type        = bool
  default     = true
}

variable "managedactions_preferred_start_time" {
  description = "Configure a maintenance window for managed actions in UTC"
  type        = string
  default     = "Sun:10:00"
}

# aws:elasticbeanstalk:managedactions:platformupdate
variable "managedactions_platformupdate_update_level" {
  description = "The highest level of update to apply with managed platform updates"
  type        = string
  default     = "minor"
}

variable "managedactions_platformupdate_instance_refresh_enabled" {
  description = "Enable weekly instance replacement."
  type        = bool
  default     = true
}

# aws:autoscaling:asg
variable "autoscaling_asg_minsize" {
  description = "Minumum instances to launch"
  type        = number
  default     = 1
}

variable "autoscaling_asg_maxsize" {
  description = "Maximum instances to launch"
  type        = number
  default     = 2
}

# aws:autoscaling:trigger
variable "autoscaling_trigger_measure_name" {
  description = "Metric used for your Auto Scaling trigger"
  type        = string
  default     = "CPUUtilization"
}

variable "autoscaling_trigger_statistic" {
  description = "Statistic the trigger should use, such as Average"
  type        = string
  default     = "Average"
}

variable "autoscaling_trigger_unit" {
  description = "Unit for the trigger measurement, such as Bytes"
  type        = string
  default     = "Percent"
}

variable "autoscaling_trigger_lower_threshold" {
  description = "Minimum level of autoscale metric to remove an instance"
  type        = number
  default     = 20
}

variable "autoscaling_trigger_lower_breach_scale_increment" {
  description = "How many Amazon EC2 instances to remove when performing a scaling activity."
  type        = number
  default     = -1
}

variable "autoscaling_trigger_upper_threshold" {
  description = "Maximum level of autoscale metric to add an instance"
  type        = number
  default     = 80
}

variable "autoscaling_trigger_upper_breach_scale_increment" {
  description = "How many Amazon EC2 instances to add when performing a scaling activity"
  type        = number
  default     = 1
}

# aws:elasticbeanstalk:hostmanager
variable "hostmanager_log_publication_control" {
  description = "Copy the log files for your application's Amazon EC2 instances to the Amazon S3 bucket associated with your application"
  type        = bool
  default     = true
}

# aws:elasticbeanstalk:cloudwatch:logs
variable "cloudwatch_logs_stream_logs" {
  description = "Whether to create groups in CloudWatch Logs for proxy and deployment logs, and stream logs from each instance in your environment"
  type        = bool
  default     = true
}

variable "cloudwatch_logs_delete_on_terminate" {
  description = "Whether to delete the log groups when the environment is terminated. If false, the logs are kept RetentionInDays days"
  type        = bool
  default     = true
}

variable "cloudwatch_logs_retention_in_days" {
  description = "The number of days to keep log events before they expire."
  type        = number
  default     = 3
}

# aws:elasticbeanstalk:cloudwatch:logs:health
variable "cloudwatch_logs_health_health_streaming_enabled" {
  description = "For environments with enhanced health reporting enabled, whether to create a group in CloudWatch Logs for environment health and archive Elastic Beanstalk environment health data. For information about enabling enhanced health, see aws:elasticbeanstalk:healthreporting:system."
  type        = bool
  default     = true
}

variable "cloudwatch_logs_health_delete_on_terminate" {
  description = "Whether to delete the log group when the environment is terminated. If false, the health data is kept RetentionInDays days."
  type        = bool
  default     = true
}

variable "cloudwatch_logs_health_retention_in_days" {
  description = "The number of days to keep the archived health data before it expires."
  type        = number
  default     = 3
}

variable "environment_type" {
  description = "Environment type, e.g. 'LoadBalanced' or 'SingleInstance'. If setting to 'SingleInstance', `rolling_update_type` must be set to 'Time', `updating_min_in_service` must be set to 0, and `loadbalancer_subnets` will be unused (it applies to the ELB, which does not exist in SingleInstance environments)."
  type        = string
  default     = "LoadBalanced"
}

# aws:elasticbeanstalk:application:environment
variable "environment_variables" {
  description = "Map of custom ENV variables to be provided to the application."
  type        = map(string)
  default     = {}
}
