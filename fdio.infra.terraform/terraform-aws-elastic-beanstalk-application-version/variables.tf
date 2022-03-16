variable "application_description" {
  description = "Short description of the Application Version."
  type        = string
  default     = "Beanstalk Application"
}

variable "application_name" {
  description = "Name of the Beanstalk Application the version is associated."
  type        = string
  default     = "Beanstalk"
}

variable "application_version_name" {
  description = "Unique name for the this Application Version."
  type        = string
  default     = "Beanstalk Version"
}
