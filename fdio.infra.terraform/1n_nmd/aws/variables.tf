variable "aws_access_key" {
  sensitive = true
}

variable "aws_secret_key" {
  sensitive = true
}

variable "name" {
  default = "dynamic-aws-creds-vault-admin"
}
