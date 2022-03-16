variable "region" {
  description = "AWS Region."
  type        = string
  default     = "us-east-1"
}

variable "application_description" {
  description = "Short description of the application."
  type        = string
  default     = "Beanstalk Application"
}
