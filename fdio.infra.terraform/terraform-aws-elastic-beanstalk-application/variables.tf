# Variables for elastic beanstalk Application
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
