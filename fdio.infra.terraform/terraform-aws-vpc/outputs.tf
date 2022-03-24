output "vpc_id" {
  value       = aws_vpc.vpc.id
  description = "The ID of the VPC"
}

output "vpc_ipv6_cidr_block" {
  value       = aws_vpc.vpc.ipv6_cidr_block
  description = "IPv6 CIDR block"
}