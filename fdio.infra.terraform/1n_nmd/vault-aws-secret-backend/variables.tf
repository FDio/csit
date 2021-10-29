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
  default     = "dynamic-aws-creds-vault-fdio"
  description = "Vault path"
  type        = string
}

variable "token" {
  description = "Vault root token"
  type        = string
  sensitive   = true
}
