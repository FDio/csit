variable "application_bucket" {
  description = "The name of the bucket."
  type        = string
  default     = "elasticbeanstalk-eu-central-1"
}

variable "application_description" {
  description = "Short description of the Application Version."
  type        = string
  default     = "Beanstalk Application"
}

variable "application_name" {
  description = "Name of the Beanstalk Application."
  type        = string
  default     = "beanstalk"
}

variable "application_name_version" {
  description = "Version of the Beanstalk Application."
  type        = string
  default     = "beanstalk-1"
}

variable "application_source" {
  description = "The source file with application code."
  type        = string
  default     = "app.zip"
}
