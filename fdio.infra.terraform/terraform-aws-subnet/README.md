<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.4 |
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
| [aws_subnet.subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_vpc_ipv4_cidr_block_association.ipv4_cidr_block_association](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_ipv4_cidr_block_association) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subnet_assign_ipv6_address_on_creation"></a> [subnet\_assign\_ipv6\_address\_on\_creation](#input\_subnet\_assign\_ipv6\_address\_on\_creation) | Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address. | `bool` | `false` | no |
| <a name="input_subnet_availability_zone"></a> [subnet\_availability\_zone](#input\_subnet\_availability\_zone) | AZ for the subnet. | `string` | `"us-east-1a"` | no |
| <a name="input_subnet_cidr_block"></a> [subnet\_cidr\_block](#input\_subnet\_cidr\_block) | The IPv4 CIDR block for the subnet. | `string` | n/a | yes |
| <a name="input_subnet_ipv6_cidr_block"></a> [subnet\_ipv6\_cidr\_block](#input\_subnet\_ipv6\_cidr\_block) | The IPv6 network range for the subnet, in CIDR notation. | `string` | n/a | yes |
| <a name="input_subnet_map_public_ip_on_launch"></a> [subnet\_map\_public\_ip\_on\_launch](#input\_subnet\_map\_public\_ip\_on\_launch) | Specify true to indicate that instances launched into the subnet should be assigned a public IP address. | `bool` | `false` | no |
| <a name="input_subnet_vpc_id"></a> [subnet\_vpc\_id](#input\_subnet\_vpc\_id) | The VPC ID. | `string` | n/a | yes |
| <a name="input_tags_environment"></a> [tags\_environment](#input\_tags\_environment) | Environment used for tag. | `string` | `""` | no |
| <a name="input_tags_name"></a> [tags\_name](#input\_tags\_name) | Name used for tag. | `string` | `""` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_subnet_id"></a> [subnet\_id](#output\_subnet\_id) | The ID of the Subnet |
<!-- END_TF_DOCS -->