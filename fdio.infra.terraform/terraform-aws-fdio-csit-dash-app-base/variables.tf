variable "application_bucket" {
  description = "The name of the bucket."
  type        = string
  default     = "elasticbeanstalk-us-east-1-407116685360"
}

variable "application_description" {
  description = "Short description of the Application Version."
  type        = string
  default     = "FD.io CDASH"
}

variable "application_name" {
  description = "Name of the Beanstalk Application."
  type        = string
  default     = "fdio-csit-dash-app-m8g"
}

variable "application_source" {
  description = "The source file with application code."
  type        = string
  default     = "../../csit.infra.dash/app.zip"
}

variable "application_version" {
  description = "Application version string."
  type        = number
  default     = 1
}
