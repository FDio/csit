<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.12.1 |
| <a name="requirement_nomad"></a> [nomad](#requirement\_nomad) | >= 2.5.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_nomad"></a> [nomad](#provider\_nomad) | 2.5.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [nomad_job.gha-dispatcher](https://registry.terraform.io/providers/hashicorp/nomad/latest/docs/resources/job) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cpu"></a> [cpu](#input\_cpu) | Specifies the CPU required to run this task in MHz. | `number` | `12000` | no |
| <a name="input_datacenters"></a> [datacenters](#input\_datacenters) | Specifies the list of DCs to be considered placing this task. | `list(string)` | <pre>[<br/>  "yul1"<br/>]</pre> | no |
| <a name="input_dispatchers"></a> [dispatchers](#input\_dispatchers) | n/a | <pre>list(object({<br/>    namespace  = string<br/>    repository = string<br/>  }))</pre> | <pre>[<br/>  {<br/>    "namespace": "sandbox",<br/>    "repository": "fdio-csit"<br/>  },<br/>  {<br/>    "namespace": "prod",<br/>    "repository": "fdio-csit"<br/>  }<br/>]</pre> | no |
| <a name="input_image"></a> [image](#input\_image) | Specifies the Docker image to run. | `string` | `"pmikus/docker-gha-dispatcher"` | no |
| <a name="input_job_name"></a> [job\_name](#input\_job\_name) | Specifies a name for the job. | `string` | `"gha-dispatcher"` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Specifies the memory required in MB. | `number` | `8000` | no |
| <a name="input_node_pool"></a> [node\_pool](#input\_node\_pool) | Specifies the node pool to place the job in. | `string` | `"default"` | no |
| <a name="input_region"></a> [region](#input\_region) | The region in which to execute the job. | `string` | `"global"` | no |
| <a name="input_type"></a> [type](#input\_type) | Specifies the Nomad scheduler to use. | `string` | `"service"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->