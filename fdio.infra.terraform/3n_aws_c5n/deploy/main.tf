data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault-name}-path"
  role    = "${var.vault-name}-role"
}

resource "aws_vpc" "CSITVPC" {
  assign_generated_ipv6_cidr_block = false
  enable_dns_hostnames             = false
  enable_dns_support               = true
  cidr_block                       = var.vpc_cidr_mgmt
  instance_tenancy                 = "default"

  tags = {
    "Name"        = "${var.resources_name_prefix}_${var.testbed_name}-vpc"
    "Environment" = var.environment_name
  }
}

resource "aws_security_group" "CSITSG" {
  depends_on                       = [
    aws_vpc.CSITVPC
  ]
  description                      = "Allow inbound traffic"
  name                             = "${var.resources_name_prefix}_${var.testbed_name}-sg"
  revoke_rules_on_delete           = false
  vpc_id                           = aws_vpc.CSITVPC.id

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
  }

  ingress {
    from_port        = 0
    to_port          = 0
    protocol         = -1
    self             = true
    ipv6_cidr_blocks = []
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
  }

  tags = {
    "Name"        = "${var.resources_name_prefix}_${var.testbed_name}-sg"
    "Environment" = var.environment_name
  }
}

resource "aws_vpc_ipv4_cidr_block_association" "b" {
  depends_on = [
    aws_vpc.CSITVPC
  ]
  cidr_block = var.vpc_cidr_b
  vpc_id     = aws_vpc.CSITVPC.id
}

resource "aws_vpc_ipv4_cidr_block_association" "c" {
  depends_on = [
    aws_vpc.CSITVPC
  ]
  cidr_block = var.vpc_cidr_c
  vpc_id     = aws_vpc.CSITVPC.id
}

resource "aws_vpc_ipv4_cidr_block_association" "d" {
  depends_on = [
    aws_vpc.CSITVPC
  ]
  cidr_block = var.vpc_cidr_d
  vpc_id     = aws_vpc.CSITVPC.id
}

# Subnets
resource "aws_subnet" "mgmt" {
  availability_zone               = var.avail_zone
  assign_ipv6_address_on_creation = false
  cidr_block                      = var.vpc_cidr_mgmt
  depends_on                      = [
    aws_vpc.CSITVPC
  ]
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.CSITVPC.id

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_subnet" "b" {
  availability_zone               = var.avail_zone
  assign_ipv6_address_on_creation = false
  cidr_block                      = var.vpc_cidr_b
  depends_on                      = [
    aws_vpc.CSITVPC,
    aws_vpc_ipv4_cidr_block_association.b
  ]
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.CSITVPC.id

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_subnet" "c" {
  availability_zone               = var.avail_zone
  assign_ipv6_address_on_creation = false
  cidr_block                      = var.vpc_cidr_c
  depends_on                      = [
    aws_vpc.CSITVPC,
    aws_vpc_ipv4_cidr_block_association.c
  ]
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.CSITVPC.id

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_subnet" "d" {
  vpc_id            = aws_vpc.CSITVPC.id
  cidr_block        = var.vpc_cidr_d
  availability_zone = var.avail_zone
  depends_on        = [aws_vpc.CSITVPC, aws_vpc_ipv4_cidr_block_association.d]

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_subnet" "d" {
  availability_zone               = var.avail_zone
  assign_ipv6_address_on_creation = false
  cidr_block                      = var.vpc_cidr_d
  depends_on                      = [
    aws_vpc.CSITVPC,
    aws_vpc_ipv4_cidr_block_association.d
  ]
  map_public_ip_on_launch         = false
  vpc_id                          = aws_vpc.CSITVPC.id

  tags = {
    "Environment" = var.environment_name
  }
}

# SSH keypair
# Temporary key for provisioning only
resource "tls_private_key" "CSITTLS" {
  algorithm   = "RSA"
  ecdsa_curve = "P521"
  rsa_bits    = 4096
}

resource "aws_key_pair" "CSITKP" {
  key_name   = "${var.resources_name_prefix}_${var.testbed_name}-key"
  public_key = "${tls_private_key.CSITTLS.public_key_openssh}"
}

resource "aws_placement_group" "CSITPG" {
  name     = "${var.resources_name_prefix}_${var.testbed_name}-pg"
  strategy = "cluster"
}

# NICs
resource "aws_network_interface" "dut1_if1" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.b,
    aws_instance.dut1
  ]
  private_ip        = var.dut1_if1_ip
  private_ips       = [var.dut1_if1_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.b.id

  attachment {
    instance     = aws_instance.dut1.id
    device_index = 1
  }

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_network_interface" "dut1_if2" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.c,
    aws_instance.dut1
  ]
  private_ip        = var.dut1_if2_ip
  private_ips       = [var.dut1_if2_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.c.id

  attachment {
    instance     = aws_instance.dut1.id
    device_index = 2
  }

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_network_interface" "dut2_if1" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.c,
    aws_instance.dut2
  ]
  private_ip        = var.dut2_if2_ip
  private_ips       = [var.dut2_if2_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.c.id

  attachment {
    instance     = aws_instance.dut2.id
    device_index = 2
  }

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_network_interface" "dut2_if2" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.d,
    aws_instance.dut2
  ]
  private_ip        = var.dut2_if2_ip
  private_ips       = [var.dut2_if2_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.d.id

  attachment {
    instance     = aws_instance.dut2.id
    device_index = 2
  }

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_network_interface" "tg_if1" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.b,
    aws_instance.tg
  ]
  private_ip        = var.tg_if1_ip
  private_ips       = [var.tg_if1_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.b.id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 1
  }

  tags = {
    "Environment" = var.environment_name
  }
}

resource "aws_network_interface" "tg_if2" {
  depends_on        = [
    aws_vpc.CSITVPC,
    aws_subnet.d,
    aws_instance.tg
  ]
  private_ip        = var.tg_if2_ip
  private_ips       = [var.tg_if2_ip]
  security_groups   = [aws_security_group.CSITSG.id]
  source_dest_check = false
  subnet_id         = aws_subnet.d.id

  attachment {
    instance     = aws_instance.tg.id
    device_index = 2
  }

  tags = {
    "Environment" = var.environment_name
  }
}

data "aws_network_interface" "dut1_if1" {
  id = aws_network_interface.dut1_if1.id
}

data "aws_network_interface" "dut1_if2" {
  id = aws_network_interface.dut1_if2.id
}

data "aws_network_interface" "dut2_if1" {
  id = aws_network_interface.dut2_if1.id
}

data "aws_network_interface" "dut2_if2" {
  id = aws_network_interface.dut2_if2.id
}

data "aws_network_interface" "tg_if1" {
  id = aws_network_interface.tg_if1.id
}

data "aws_network_interface" "tg_if2" {
  id = aws_network_interface.tg_if2.id
}

# Instances
resource "aws_instance" "tg" {
  depends_on                           = [
    aws_vpc.CSITVPC,
    aws_placement_group.CSITPG,
    aws_security_group.CSITSG
  ]
  ami                                  = var.ami_image_tg
  availability_zone                    = var.avail_zone
  associate_public_ip_address          = true
  instance_initiated_shutdown_behavior = var.instance_initiated_shutdown_behavior
  instance_type                        = var.instance_type
  key_name                             = aws_key_pair.CSITKP.key_name
  placement_group                      = aws_placement_group.CSITPG.id
  private_ip                           = var.tg_mgmt_ip
  source_dest_check                    = false
  subnet_id                            = aws_subnet.mgmt.id
  vpc_security_group_ids               = [aws_security_group.CSITSG.id]
  # host_id                            = "1"

#  root_block_device {
#    volume_size = 50
#  }

  tags = {
    "Name"        = "${var.resources_name_prefix}_${var.testbed_name}-tg"
    "Environment" = var.environment_name
  }
}

resource "aws_instance" "dut1" {
  depends_on = [
    aws_vpc.CSITVPC,
    aws_placement_group.CSITPG,
    aws_instance.tg
  ]
  ami                                  = var.ami_image_sut
  availability_zone                    = var.avail_zone
  associate_public_ip_address          = true
  instance_initiated_shutdown_behavior = var.instance_initiated_shutdown_behavior
  instance_type                        = var.instance_type
  key_name                             = aws_key_pair.CSITKP.key_name
  placement_group                      = aws_placement_group.CSITPG.id
  private_ip                           = var.dut1_mgmt_ip
  source_dest_check                    = false
  subnet_id                            = aws_subnet.mgmt.id
  vpc_security_group_ids               = [aws_security_group.CSITSG.id]
  # host_id                            = "2"

#  root_block_device {
#    volume_size = 50
#  }

  tags = {
    "Name"        = "${var.resources_name_prefix}_${var.testbed_name}-dut1"
    "Environment" = var.environment_name
  }
}

resource "aws_instance" "dut2" {
  depends_on = [
    aws_vpc.CSITVPC,
    aws_placement_group.CSITPG,
    aws_instance.tg,
    aws_instance.dut1
  ]
  ami                                  = var.ami_image_sut
  availability_zone                    = var.avail_zone
  associate_public_ip_address          = true
  instance_initiated_shutdown_behavior = var.instance_initiated_shutdown_behavior
  instance_type                        = var.instance_type
  key_name                             = aws_key_pair.CSITKP.key_name
  placement_group                      = aws_placement_group.CSITPG.id
  private_ip                           = var.dut2_mgmt_ip
  source_dest_check                    = false
  subnet_id                            = aws_subnet.mgmt.id
  vpc_security_group_ids               = [aws_security_group.CSITSG.id]
  # host_id                            = "3"

#  root_block_device {
#    volume_size = 50
#  }

  tags = {
    "Name"        = "${var.resources_name_prefix}_${var.testbed_name}-dut2"
    "Environment" = var.environment_name
  }
}

# Routes
resource "aws_route" "CSIT-igw" {
  depends_on             = [
    aws_vpc.CSITVPC,
    aws_internet_gateway.CSITGW
  ]
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.CSITGW.id
  route_table_id         = aws_vpc.CSITVPC.main_route_table_id
}

resource "aws_route" "dummy-trex-port-0" {
  depends_on             = [
    aws_vpc.CSITVPC,
    aws_instance.dut1
  ]
  destination_cidr_block = var.trex_dummy_cidr_port_0
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = aws_vpc.CSITVPC.main_route_table_id
}

resource "aws_route" "dummy-trex-port-1" {
  depends_on             = [
    aws_vpc.CSITVPC,
    aws_instance.dut1
  ]
  destination_cidr_block = var.trex_dummy_cidr_port_1
  network_interface_id   = aws_instance.tg.primary_network_interface_id
  route_table_id         = aws_vpc.CSITVPC.main_route_table_id
}

# Deployment/Ansible
resource "null_resource" "deploy_tg" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2,
    aws_instance.dut1,
    aws_network_interface.dut1_if1,
    aws_network_interface.dut1_if2,
    aws_instance.dut2,
    aws_network_interface.dut2_if1,
    aws_network_interface.dut2_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.tg.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }

#  provisioner "ansible" {
#    plays {
#      playbook {
#        file_path      = var.ansible_file_path
#        force_handlers = true
#      }
#      hosts = ["tg_aws"]
#      extra_vars = {
#        ansible_ssh_pass           = var.ansible_provision_pwd
#        ansible_python_interpreter = var.ansible_python_executable
#        aws                        = true
#      }
#    }
#  }
#
#  provisioner "remote-exec" {
#    on_failure = continue
#    inline     = ["sudo reboot"]
#  }
}

resource "null_resource" "deploy_dut1" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2,
    aws_instance.dut1,
    aws_network_interface.dut1_if1,
    aws_network_interface.dut1_if2,
    aws_instance.dut2,
    aws_network_interface.dut2_if1,
    aws_network_interface.dut2_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.dut1.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }

#  provisioner "ansible" {
#    plays {
#      playbook {
#        file_path      = var.ansible_file_path
#        force_handlers = true
#      }
#      hosts = ["sut_aws"]
#      extra_vars = {
#        ansible_ssh_pass           = var.ansible_provision_pwd
#        ansible_python_interpreter = var.ansible_python_executable
#        aws                        = true
#      }
#    }
#  }
#
#  provisioner "remote-exec" {
#    on_failure = continue
#    inline     = ["sudo reboot"]
#  }
}

resource "null_resource" "deploy_dut2" {
  depends_on = [
    aws_instance.tg,
    aws_network_interface.tg_if1,
    aws_network_interface.tg_if2,
    aws_instance.dut1,
    aws_network_interface.dut1_if1,
    aws_network_interface.dut1_if2,
    aws_instance.dut2,
    aws_network_interface.dut2_if1,
    aws_network_interface.dut2_if2
  ]

  connection {
    user        = "ubuntu"
    host        = aws_instance.dut2.public_ip
    private_key = tls_private_key.CSITTLS.private_key_pem
  }

  provisioner "remote-exec" {
    inline = var.first_run_commands
  }

#  provisioner "ansible" {
#    plays {
#      playbook {
#        file_path      = var.ansible_file_path
#        force_handlers = true
#      }
#      hosts = ["sut_aws"]
#      extra_vars = {
#        ansible_ssh_pass           = var.ansible_provision_pwd
#        ansible_python_interpreter = var.ansible_python_executable
#        aws                        = true
#      }
#    }
#  }
#
#  provisioner "remote-exec" {
#    on_failure = continue
#    inline     = ["sudo reboot"]
#  }
}

resource "null_resource" "deploy_topology" {
  depends_on = [
    aws_instance.tg,
    aws_instance.dut1,
    aws_instance.dut2
  ]

  provisioner "ansible" {
    plays {
      playbook {
        file_path = var.ansible_topology_path
      }
      hosts = ["local"]
      extra_vars = {
        ansible_python_interpreter = var.ansible_python_executable
        testbed_name               = var.testbed_name
        cloud_topology             = var.topology_name
        tg_if1_mac                 = data.aws_network_interface.tg_if1.mac_address
        tg_if2_mac                 = data.aws_network_interface.tg_if2.mac_address
        dut1_if1_mac               = data.aws_network_interface.dut1_if1.mac_address
        dut1_if2_mac               = data.aws_network_interface.dut1_if2.mac_address
        dut2_if1_mac               = data.aws_network_interface.dut2_if1.mac_address
        dut2_if2_mac               = data.aws_network_interface.dut2_if2.mac_address
        tg_public_ip               = aws_instance.tg.public_ip
        dut1_public_ip             = aws_instance.dut1.public_ip
        dut2_public_ip             = aws_instance.dut2.public_ip
        public_ip_list             = "${aws_instance.tg.public_ip},${aws_instance.dut1.public_ip},${aws_instance.dut2.public_ip}"
      }
    }
  }
}
