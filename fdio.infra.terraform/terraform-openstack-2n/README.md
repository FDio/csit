# terraform-openstack-2n-generic
Terraform module to create 2n-generic topology.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.4.2 |
| <a name="requirement_openstack"></a> [openstack](#requirement\_openstack) | ~> 1.53.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_local"></a> [local](#provider\_local) | 2.4.1 |
| <a name="provider_openstack"></a> [openstack](#provider\_openstack) | 1.53.0 |
| <a name="provider_template"></a> [template](#provider\_template) | 2.2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_openstack_compute_keypair_v2"></a> [openstack\_compute\_keypair\_v2](#module\_openstack\_compute\_keypair\_v2) | pmikus/compute-keypair-v2/openstack | 1.54.1 |
| <a name="module_openstack_images_image_v2"></a> [openstack\_images\_image\_v2](#module\_openstack\_images\_image\_v2) | pmikus/images-image-v2/openstack | 1.54.1 |
| <a name="module_sut1"></a> [sut1](#module\_sut1) | pmikus/compute-instance-v2/openstack | 1.54.1 |
| <a name="module_tg1"></a> [tg1](#module\_tg1) | pmikus/compute-instance-v2/openstack | 1.54.1 |

## Resources

| Name | Type |
|------|------|
| [local_file.hosts](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.topology_file](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [openstack_networking_port_v2.port_sut1_data1](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [openstack_networking_port_v2.port_sut1_data2](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [openstack_networking_port_v2.port_sut1_mgmt](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [openstack_networking_port_v2.port_tg1_data1](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [openstack_networking_port_v2.port_tg1_data2](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [openstack_networking_port_v2.port_tg1_mgmt](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs/resources/networking_port_v2) | resource |
| [template_cloudinit_config.cloudinit_config_sut1](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/cloudinit_config) | data source |
| [template_cloudinit_config.cloudinit_config_tg1](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/cloudinit_config) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_flavour_name"></a> [flavour\_name](#input\_flavour\_name) | (Optional; Required if flavor\_id is empty) The name of the desired flavor for the server. Changing this resizes the existing server. | `string` | n/a | yes |
| <a name="input_network_id_data"></a> [network\_id\_data](#input\_network\_id\_data) | (Required) The ID of the network to attach the port to. Changing this creates a new port. | `string` | n/a | yes |
| <a name="input_network_id_mgmt"></a> [network\_id\_mgmt](#input\_network\_id\_mgmt) | (Required) The ID of the network to attach the port to. Changing this creates a new port. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_sut_id"></a> [sut\_id](#output\_sut\_id) | SUT VM ID. |
| <a name="output_tg_id"></a> [tg\_id](#output\_tg\_id) | TG VM ID. |
<!-- END_TF_DOCS -->
