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
| [aws_elastic_beanstalk_application_version.application_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elastic_beanstalk_application_version) | resource |
| [aws_s3_bucket.bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_object.object](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_application_description"></a> [application\_description](#input\_application\_description) | Short description of the Application Version. | `string` | `"Beanstalk Application"` | no |
| <a name="input_application_name"></a> [application\_name](#input\_application\_name) | Name of the Beanstalk Application the version is associated. | `string` | `"Beanstalk"` | no |
| <a name="input_application_version_name"></a> [application\_version\_name](#input\_application\_version\_name) | Unique name for the this Application Version. | `string` | `"Beanstalk Version"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->