variable "region" {
  description = "AWS Region."
  type        = string
  default     = "us-east-1"
}

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
