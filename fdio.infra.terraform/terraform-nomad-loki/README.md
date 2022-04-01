<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.1.4 |
| <a name="requirement_nomad"></a> [nomad](#requirement\_nomad) | >= 1.4.16 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_nomad"></a> [nomad](#provider\_nomad) | 1.4.16 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [nomad_job.nomad_job_prometheus](https://registry.terraform.io/providers/hashicorp/nomad/latest/docs/resources/job) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_auto_promote"></a> [auto\_promote](#input\_auto\_promote) | Specifies if the job should auto-promote to the canary version | `bool` | `true` | no |
| <a name="input_auto_revert"></a> [auto\_revert](#input\_auto\_revert) | Specifies if the job should auto-revert to the last stable job | `bool` | `true` | no |
| <a name="input_canary"></a> [canary](#input\_canary) | Equal to the count of the task group allows blue/green depl. | `number` | `1` | no |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | CPU allocation | `number` | `2000` | no |
| <a name="input_data_dir"></a> [data\_dir](#input\_data\_dir) | Loki data dir allocation | `string` | `""` | no |
| <a name="input_datacenters"></a> [datacenters](#input\_datacenters) | Specifies the list of DCs to be considered placing this task | `list(string)` | <pre>[<br>  "dc1"<br>]</pre> | no |
| <a name="input_gl_version"></a> [gl\_version](#input\_gl\_version) | Grafana Loki version | `string` | `"2.4.2"` | no |
| <a name="input_group_count"></a> [group\_count](#input\_group\_count) | Specifies the number of the task groups running under this one | `number` | `1` | no |
| <a name="input_job_name"></a> [job\_name](#input\_job\_name) | Specifies a name for the job | `string` | `"loki"` | no |
| <a name="input_max_parallel"></a> [max\_parallel](#input\_max\_parallel) | Specifies the maximum number of updates to perform in parallel | `number` | `1` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Specifies the memory required in MB | `number` | `4096` | no |
| <a name="input_port"></a> [port](#input\_port) | Specifies the static TCP/UDP port to allocate | `number` | `3100` | no |
| <a name="input_region"></a> [region](#input\_region) | Specifies the list of DCs to be considered placing this task | `string` | `"global"` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Specifies the name this service will be advertised in Consul | `string` | `"loki"` | no |
| <a name="input_use_canary"></a> [use\_canary](#input\_use\_canary) | Uses canary deployment | `bool` | `true` | no |
| <a name="input_use_host_volume"></a> [use\_host\_volume](#input\_use\_host\_volume) | Use Nomad host volume feature | `bool` | `false` | no |
| <a name="input_vault_secret"></a> [vault\_secret](#input\_vault\_secret) | Set of properties to be able to fetch secret from vault. | <pre>object({<br>    use_vault_provider        = bool,<br>    vault_kv_policy_name      = string,<br>    vault_kv_path             = string,<br>    vault_kv_field_access_key = string,<br>    vault_kv_field_secret_key = string<br>  })</pre> | <pre>{<br>  "use_vault_provider": false,<br>  "vault_kv_field_access_key": "access_key",<br>  "vault_kv_field_secret_key": "secret_key",<br>  "vault_kv_path": "secret/data/prometheus",<br>  "vault_kv_policy_name": "kv"<br>}</pre> | no |
| <a name="input_volume_destination"></a> [volume\_destination](#input\_volume\_destination) | Specifies where the volume should be mounted inside the task | `string` | `""` | no |
| <a name="input_volume_source"></a> [volume\_source](#input\_volume\_source) | The name of the volume to request | `string` | `""` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->