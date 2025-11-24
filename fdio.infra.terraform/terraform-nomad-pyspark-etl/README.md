<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.12.1 |
| <a name="requirement_nomad"></a> [nomad](#requirement\_nomad) | >= 2.5.2 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_nomad"></a> [nomad](#provider\_nomad) | 2.5.2 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [nomad_job.nomad_job](https://registry.terraform.io/providers/hashicorp/nomad/latest/docs/resources/job) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_nomad_acl"></a> [nomad\_acl](#input\_nomad\_acl) | Nomad ACLs enabled/disabled. | `bool` | `false` | no |
| <a name="input_nomad_jobs"></a> [nomad\_jobs](#input\_nomad\_jobs) | List of ETL jobs | `list(map(any))` | <pre>[<br/>  {<br/>    "job_name": "etl-stats",<br/>    "memory": 50000,<br/>    "script_name": "stats"<br/>  },<br/>  {<br/>    "job_name": "etl-trending-hoststack",<br/>    "memory": 50000,<br/>    "script_name": "trending_hoststack"<br/>  },<br/>  {<br/>    "job_name": "etl-trending-mrr",<br/>    "memory": 60000,<br/>    "script_name": "trending_mrr"<br/>  },<br/>  {<br/>    "job_name": "etl-trending-ndrpdr",<br/>    "memory": 60000,<br/>    "script_name": "trending_ndrpdr"<br/>  },<br/>  {<br/>    "job_name": "etl-trending-soak",<br/>    "memory": 60000,<br/>    "script_name": "trending_soak"<br/>  }<br/>]</pre> | no |
| <a name="input_nomad_provider_ca_file"></a> [nomad\_provider\_ca\_file](#input\_nomad\_provider\_ca\_file) | A local file path to a PEM-encoded certificate authority. | `string` | `"/etc/nomad.d/ssl/nomad-ca.pem"` | no |
| <a name="input_nomad_provider_cert_file"></a> [nomad\_provider\_cert\_file](#input\_nomad\_provider\_cert\_file) | A local file path to a PEM-encoded certificate. | `string` | `"/etc/nomad.d/ssl/nomad.pem"` | no |
| <a name="input_nomad_provider_key_file"></a> [nomad\_provider\_key\_file](#input\_nomad\_provider\_key\_file) | A local file path to a PEM-encoded private key. | `string` | `"/etc/nomad.d/ssl/nomad-key.pem"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->