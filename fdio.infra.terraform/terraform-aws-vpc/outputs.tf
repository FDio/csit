output "vpc_id" {
  value       = aws_vpc.vpc.id
  description = "The ID of the VPC."
}

output "vpc_ipv6_cidr_block" {
  value       = aws_vpc.vpc.ipv6_cidr_block
  description = "IPv6 CIDR block."
}

output "vpc_main_route_table_id" {
  value       = aws_vpc.vpc.main_route_table_id
  description = "The ID of the Main Route Table."
}

output "vpc_subnet_id" {
  value       = aws_subnet.subnet.id
  description = "The ID of the Subnet."
}

output "vpc_security_group_id" {
  value       = aws_security_group.security_group.id
  description = "The ID of the Security Group."
}
