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
| [aws_internet_gateway.internet_gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway) | resource |
| [aws_route.route](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route) | resource |
| [aws_security_group.security_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_subnet.subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_vpc.vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_security_group_description"></a> [security\_group\_description](#input\_security\_group\_description) | Security group description. | `string` | `"Allow inbound/outbound traffic"` | no |
| <a name="input_security_group_egress"></a> [security\_group\_egress](#input\_security\_group\_egress) | Egress security group map. | `list(any)` | <pre>[<br>  {<br>    "cidr_blocks": [<br>      "0.0.0.0/0"<br>    ],<br>    "from_port": 0,<br>    "ipv6_cidr_blocks": [<br>      "::/0"<br>    ],<br>    "protocol": "-1",<br>    "to_port": 0<br>  }<br>]</pre> | no |
| <a name="input_security_group_ingress"></a> [security\_group\_ingress](#input\_security\_group\_ingress) | Ingress security group map. | `list(any)` | <pre>[<br>  {<br>    "cidr_blocks": [<br>      "0.0.0.0/0"<br>    ],<br>    "from_port": 22,<br>    "ipv6_cidr_blocks": [<br>      "::/0"<br>    ],<br>    "protocol": "tcp",<br>    "self": false,<br>    "to_port": 22<br>  },<br>  {<br>    "cidr_blocks": [<br>      "0.0.0.0/0"<br>    ],<br>    "from_port": 0,<br>    "ipv6_cidr_blocks": [<br>      "::/0"<br>    ],<br>    "protocol": -1,<br>    "self": true,<br>    "to_port": 0<br>  }<br>]</pre> | no |
| <a name="input_security_group_name"></a> [security\_group\_name](#input\_security\_group\_name) | Name of the security group. | `string` | n/a | yes |
| <a name="input_security_group_revoke_rules_on_delete"></a> [security\_group\_revoke\_rules\_on\_delete](#input\_security\_group\_revoke\_rules\_on\_delete) | Instruct Terraform to revoke all of the Security Groups attached ingress and egress rules before deleting the rule itself. | `bool` | `false` | no |
| <a name="input_subnet_assign_ipv6_address_on_creation"></a> [subnet\_assign\_ipv6\_address\_on\_creation](#input\_subnet\_assign\_ipv6\_address\_on\_creation) | Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address. | `bool` | `false` | no |
| <a name="input_subnet_availability_zone"></a> [subnet\_availability\_zone](#input\_subnet\_availability\_zone) | AWS availability zone | `string` | `"us-east-1a"` | no |
| <a name="input_subnet_map_public_ip_on_launch"></a> [subnet\_map\_public\_ip\_on\_launch](#input\_subnet\_map\_public\_ip\_on\_launch) | Specify true to indicate that instances launched into the subnet should be assigned a public IP address. | `bool` | `false` | no |
| <a name="input_tags_environment"></a> [tags\_environment](#input\_tags\_environment) | Environment used for tag. | `string` | `""` | no |
| <a name="input_tags_name"></a> [tags\_name](#input\_tags\_name) | Name used for tag. | `string` | `""` | no |
| <a name="input_vpc_assign_generated_ipv6_cidr_block"></a> [vpc\_assign\_generated\_ipv6\_cidr\_block](#input\_vpc\_assign\_generated\_ipv6\_cidr\_block) | Requests an Amazon-provided IPv6 CIDR block with a /56 prefix length for the VPC. | `bool` | `true` | no |
| <a name="input_vpc_cidr_block"></a> [vpc\_cidr\_block](#input\_vpc\_cidr\_block) | The CIDR block for the association. | `string` | `"192.168.0.0/24"` | no |
| <a name="input_vpc_enable_dns_hostnames"></a> [vpc\_enable\_dns\_hostnames](#input\_vpc\_enable\_dns\_hostnames) | Whether or not the VPC has DNS hostname support. | `bool` | `true` | no |
| <a name="input_vpc_enable_dns_support"></a> [vpc\_enable\_dns\_support](#input\_vpc\_enable\_dns\_support) | Whether or not the VPC has DNS support. | `bool` | `true` | no |
| <a name="input_vpc_instance_tenancy"></a> [vpc\_instance\_tenancy](#input\_vpc\_instance\_tenancy) | The allowed tenancy of instances launched into the selected VPC. | `string` | `"default"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_vpc_id"></a> [vpc\_id](#output\_vpc\_id) | The ID of the VPC. |
| <a name="output_vpc_ipv6_cidr_block"></a> [vpc\_ipv6\_cidr\_block](#output\_vpc\_ipv6\_cidr\_block) | IPv6 CIDR block. |
| <a name="output_vpc_main_route_table_id"></a> [vpc\_main\_route\_table\_id](#output\_vpc\_main\_route\_table\_id) | The ID of the Main Route Table. |
| <a name="output_vpc_security_group_id"></a> [vpc\_security\_group\_id](#output\_vpc\_security\_group\_id) | The ID of the Security Group. |
| <a name="output_vpc_subnet_id"></a> [vpc\_subnet\_id](#output\_vpc\_subnet\_id) | The ID of the Subnet. |
<!-- END_TF_DOCS -->