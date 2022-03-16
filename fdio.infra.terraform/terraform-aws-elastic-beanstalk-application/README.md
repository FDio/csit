<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.4 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 4.3.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_elastic_beanstalk_application.application](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elastic_beanstalk_application) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_application_description"></a> [application\_description](#input\_application\_description) | Short description of the application. | `string` | `"Beanstalk Application"` | no |
| <a name="input_application_name"></a> [application\_name](#input\_application\_name) | The name of the application, must be unique within account. | `string` | `"Beanstalk"` | no |
| <a name="input_appversion_lifecycle_delete_source_from_s3"></a> [appversion\_lifecycle\_delete\_source\_from\_s3](#input\_appversion\_lifecycle\_delete\_source\_from\_s3) | Whether to delete application versions from S3 source. | `bool` | `false` | no |
| <a name="input_appversion_lifecycle_max_count"></a> [appversion\_lifecycle\_max\_count](#input\_appversion\_lifecycle\_max\_count) | The max number of application versions to keep. | `number` | `2` | no |
| <a name="input_appversion_lifecycle_service_role_arn"></a> [appversion\_lifecycle\_service\_role\_arn](#input\_appversion\_lifecycle\_service\_role\_arn) | The service role ARN to use for application version cleanup. If left empty, the `appversion_lifecycle` block will not be created. | `string` | `""` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application_description"></a> [application\_description](#output\_application\_description) | n/a |
| <a name="output_application_name"></a> [application\_name](#output\_application\_name) | n/a |
<!-- END_TF_DOCS -->