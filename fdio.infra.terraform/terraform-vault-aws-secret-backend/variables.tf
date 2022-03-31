variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}

variable "name" {
  default     = "dynamic-aws-creds-vault"
  description = "Vault path"
  type        = string
}
