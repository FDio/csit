variable "elasticapp_description" {
  description = "Short description of the application."
  type        = string
  default     = "FD.io CSIT Results Dashboard"
}

variable "elasticapp_name" {
  description = "The name of the application, must be unique within account."
  type        = string
  default     = "fdio_csit_dash"
}

variable "elasticenv_elb_public_subnets" {
  description = "Elastic Beanstalk Environment variable."
  type        = list
}

variable "elasticenv_instance_type" {
  description = "Elastic Beanstalk Environment variable."
  type        = string
  default     = "t3.medium"
}

variable "elasticenv_minsize" {
  description = "Elastic Beanstalk Environment variable."
  type        = number
  default     = 1
}

variable "elasticenv_maxsize" {
  description = "Elastic Beanstalk Environment variable."
  type        = number
  default     = 2
}

variable "elasticenv_name" {
  description = "A unique name for this Environment variable."
  type        = string
  default     = "csit-dash"
}

variable "elasticenv_public_subnets" {
  description = "Elastic Beanstalk Environment tier."
  type        = list
}

variable "elasticenv_solution_stack_name_regex" {
  description = "A regex string to apply to the solution stack list returned by AWS."
  type        = string
  default     = "^64bit Amazon Linux 2 (.*) running Python 3.8(.*)$"
}

variable "elasticenv_solution_stack_most_recent" {
  description = "If more than one result is returned, use the most recent solution stack."
  type        = bool
  default     = true
}

variable "elasticenv_tier" {
  description = "The environment tier specified"
  type        = string
  default     = "WebServer"
}

variable "elasticenv_vpc_id" {
  description = "Elastic Beanstalk Environment tier."
  type        = string
  default     = "vpc-csit-dash"
}

variable "aws_access_key_id" {
  description = "AWS access key."
  type        = string
  default     = "aws"
}

variable "aws_secret_access_key" {
  description = "AWS secret key."
  type        = string
  default     = "aws"
}

variable "aws_default_region" {
  description = "AWS region."
  type        = string
  default     = "aws"
}
