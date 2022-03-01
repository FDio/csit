variable "elasticapp_description" {
  description = "Short description of the application."
  type        = string
  default     = "Beanstalk Application"
}

variable "elasticapp_name" {
  description = "The name of the application, must be unique within account."
  type        = string
  default     = "Beanstalk"
}

variable "elasticenv_description" {
  description = "Short description of the environment."
  type        = string
  default     = "Beanstalk Environment"
}

variable "elasticenv_elb_public_subnets" {
  description = "Elastic Beanstalk Environment variable."
  type        = list(any)
}

variable "elasticenv_environment" {
  type        = map(string)
  default     = {}
  description = "Map of custom ENV variables to be provided to the application."
}

variable "elasticenv_instance_type" {
  description = "Instances type"
  type        = string
  default     = "t3.medium"
}

variable "elasticenv_name" {
  description = "A unique name for this Environment variable."
  type        = string
  default     = "Beanstalk-env"
}

variable "elasticenv_public_subnets" {
  description = "Elastic Beanstalk Environment tier."
  type        = list(any)
}

variable "elasticenv_solution_name" {
  description = "A solution stack to base your environment off of."
  type        = string
  default     = "64bit Amazon Linux 2 v3.3.11 running Python 3.8"
}

variable "elasticenv_tier" {
  description = "The environment tier specified"
  type        = string
  default     = "WebServer"
}

variable "elasticenv_healthcheck_url" {
  description = "Application Health Check URL. Elastic Beanstalk will call this URL to check the health of the application running on EC2 instances"
  type        = string
  default     = "/"
}




variable "managedactions_managed_actions_enabled" {
  description = "Enable managed platform updates. When you set this to true, you must also specify a `PreferredStartTime` and `UpdateLevel`"
  type        = bool
  default     = true
}

variable "elasticenv_minsize" {
  description = "Minumum instances to launch"
  type        = number
  default     = 1
}

variable "elasticenv_maxsize" {
  description = "Maximum instances to launch"
  type        = number
  default     = 2
}

variable "managedactions_preferred_start_time" {
  description = "Configure a maintenance window for managed actions in UTC"
  type        = string
  default     = "Sun:10:00"
}

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

# Autoscaling
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

# Logs
variable "hostmanager_log_publication_control" {
  description = "Copy the log files for your application's Amazon EC2 instances to the Amazon S3 bucket associated with your application"
  type        = bool
  default     = false
}

variable "cloudwatch_logs_stream_logs" {
  description = "Whether to create groups in CloudWatch Logs for proxy and deployment logs, and stream logs from each instance in your environment"
  type        = bool
  default     = false
}

variable "cloudwatch_logs_delete_on_terminate" {
  description = "Whether to delete the log groups when the environment is terminated. If false, the logs are kept RetentionInDays days"
  type        = bool
  default     = false
}

variable "cloudwatch_logs_retention_in_days" {
  description = "The number of days to keep log events before they expire."
  type        = number
  default     = 7
}

variable "cloudwatch_logs_health_streaming_enabled" {
  description = "For environments with enhanced health reporting enabled, whether to create a group in CloudWatch Logs for environment health and archive Elastic Beanstalk environment health data. For information about enabling enhanced health, see aws:elasticbeanstalk:healthreporting:system."
  type        = bool
  default     = false
}

variable "cloudwatch_logs_health_delete_on_terminate" {
  description = "Whether to delete the log group when the environment is terminated. If false, the health data is kept RetentionInDays days."
  type        = bool
  default     = false
}

variable "cloudwatch_logs_health_retention_in_days" {
  description = "The number of days to keep the archived health data before it expires."
  type        = number
  default     = 7
}

# VPC
variable "vpc_cidr_block" {
  description = "The CIDR block for the association."
  type        = string
  default     = "192.168.0.0/24"
}

variable "vpc_instance_tenancy" {
  description = "The allowed tenancy of instances launched into the selected VPC."
  type        = string
  default     = "default"
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

variable "vpc_tags_environment" {
  description = "Environment name of the desired VPC."
  type        = string
  default     = "beanstalk"
}

variable "vpc_tags_name" {
  description = "Name of the desired VPC."
  type        = string
  default     = "beanstalk"
}
