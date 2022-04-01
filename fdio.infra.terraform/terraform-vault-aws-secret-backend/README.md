<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.4 |
| <a name="requirement_vault"></a> [vault](#requirement\_vault) | >=2.22.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_vault"></a> [vault](#provider\_vault) | >=2.22.1 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [vault_aws_secret_backend.aws](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/aws_secret_backend) | resource |
| [vault_aws_secret_backend_role.admin](https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/aws_secret_backend_role) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_access_key"></a> [aws\_access\_key](#input\_aws\_access\_key) | AWS access key | `string` | n/a | yes |
| <a name="input_aws_secret_key"></a> [aws\_secret\_key](#input\_aws\_secret\_key) | AWS secret key | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Vault path | `string` | `"dynamic-aws-creds-vault"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_backend"></a> [backend](#output\_backend) | n/a |
| <a name="output_role"></a> [role](#output\_role) | n/a |
<!-- END_TF_DOCS -->