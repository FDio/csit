resource "vault_aws_secret_backend" "aws_secret_backend" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  path       = "${var.name}-path"

  default_lease_ttl_seconds = "0"
  max_lease_ttl_seconds     = "0"
}

resource "vault_aws_secret_backend_role" "aws_secret_backend_role" {
  backend         = vault_aws_secret_backend.aws_secret_backend.path
  name            = "${var.name}-role"
  credential_type = "iam_user"

  policy_document = var.policy_document
}

output "backend" {
  value = vault_aws_secret_backend.aws_secret_backend.path
}

output "role" {
  value = vault_aws_secret_backend_role.aws_secret_backend_role.name
}
