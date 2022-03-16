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