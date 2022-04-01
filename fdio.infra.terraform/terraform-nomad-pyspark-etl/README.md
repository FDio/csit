<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.4 |
| <a name="requirement_nomad"></a> [nomad](#requirement\_nomad) | >= 1.4.16 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_nomad"></a> [nomad](#provider\_nomad) | >= 1.4.16 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [nomad_job.nomad_job_etl](https://registry.terraform.io/providers/hashicorp/nomad/latest/docs/resources/job) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_access_key_id"></a> [aws\_access\_key\_id](#input\_aws\_access\_key\_id) | AWS access key. | `string` | `"aws"` | no |
| <a name="input_aws_default_region"></a> [aws\_default\_region](#input\_aws\_default\_region) | AWS region | `string` | `"aws"` | no |
| <a name="input_aws_secret_access_key"></a> [aws\_secret\_access\_key](#input\_aws\_secret\_access\_key) | AWS secret key | `string` | `"aws"` | no |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | Specifies the CPU required to run this task in MHz. | `number` | `10000` | no |
| <a name="input_cron"></a> [cron](#input\_cron) | Specifies a cron expression configuring the interval to launch. | `string` | `"@daily"` | no |
| <a name="input_datacenters"></a> [datacenters](#input\_datacenters) | Specifies the list of DCs to be considered placing this task. | `list(string)` | <pre>[<br>  "dc1"<br>]</pre> | no |
| <a name="input_envs"></a> [envs](#input\_envs) | Specifies ETL environment variables. | `list(string)` | `[]` | no |
| <a name="input_image"></a> [image](#input\_image) | Specifies the Docker image to run. | `string` | `"pmikus/docker-ubuntu-focal-aws-glue:latest"` | no |
| <a name="input_job_name"></a> [job\_name](#input\_job\_name) | Specifies a name for the job. | `string` | `"etl"` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Specifies the memory required in MB. | `number` | `20000` | no |
| <a name="input_out_aws_access_key_id"></a> [out\_aws\_access\_key\_id](#input\_out\_aws\_access\_key\_id) | AWS access key. | `string` | `"aws"` | no |
| <a name="input_out_aws_default_region"></a> [out\_aws\_default\_region](#input\_out\_aws\_default\_region) | AWS region | `string` | `"aws"` | no |
| <a name="input_out_aws_secret_access_key"></a> [out\_aws\_secret\_access\_key](#input\_out\_aws\_secret\_access\_key) | AWS secret key | `string` | `"aws"` | no |
| <a name="input_prohibit_overlap"></a> [prohibit\_overlap](#input\_prohibit\_overlap) | Specifies if this job should wait until previous completed. | `bool` | `true` | no |
| <a name="input_time_zone"></a> [time\_zone](#input\_time\_zone) | Specifies the time zone to evaluate the next launch interval. | `string` | `"UTC"` | no |
| <a name="input_type"></a> [type](#input\_type) | Specifies the Nomad scheduler to use. | `string` | `"batch"` | no |
| <a name="input_vault_secret"></a> [vault\_secret](#input\_vault\_secret) | Set of properties to be able to fetch secret from vault. | <pre>object({<br>    use_vault_provider        = bool,<br>    vault_kv_policy_name      = string,<br>    vault_kv_path             = string,<br>    vault_kv_field_access_key = string,<br>    vault_kv_field_secret_key = string<br>  })</pre> | <pre>{<br>  "use_vault_provider": false,<br>  "vault_kv_field_access_key": "access_key",<br>  "vault_kv_field_secret_key": "secret_key",<br>  "vault_kv_path": "secret/data/etl",<br>  "vault_kv_policy_name": "kv"<br>}</pre> | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->