provider "azurerm" {
  version = ">= 1.4.0"
}

# Variables

variable "vpc_addr_space_a" {
  type = string
  default = "172.16.0.0/16"
}

variable "vpc_cidr_a" {
  type = string
  default = "172.16.0.0/24"
}

variable "vpc_cidr_b" {
  type = string
  default = "172.16.10.0/24"
}

variable "vpc_cidr_c" {
  type = string
  default = "172.16.200.0/24"
}

variable "vpc_cidr_d" {
  type = string
  default = "172.16.20.0/24"
}

variable "trex_dummy_cidr_port_0" {
  type = string
  default = "172.16.11.0/24"
}

variable "trex_dummy_cidr_port_1" {
  type = string
  default = "172.16.21.0/24"
}

# Create resource group and resources

resource "azurerm_resource_group" "CSIT" {
  name     = "CSIT"
  #location = "East US"
  location = "UK South"
}

resource "azurerm_virtual_network" "CSIT" {
  name                = "CSIT-network"
  resource_group_name = azurerm_resource_group.CSIT.name
  location            = azurerm_resource_group.CSIT.location
  address_space       = [ var.vpc_addr_space_a ]
  depends_on          = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_subnet" "a" {
  name                 = "subnet_a"
  resource_group_name  = azurerm_resource_group.CSIT.name
  virtual_network_name = azurerm_virtual_network.CSIT.name
  address_prefix       = var.vpc_cidr_a
  depends_on           = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_subnet" "b" {
  name                 = "subnet_b"
  resource_group_name  = azurerm_resource_group.CSIT.name
  virtual_network_name = azurerm_virtual_network.CSIT.name
  address_prefix       = var.vpc_cidr_b
  depends_on           = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_subnet" "c" {
  name                 = "subnet_c"
  resource_group_name  = azurerm_resource_group.CSIT.name
  virtual_network_name = azurerm_virtual_network.CSIT.name
  address_prefix       = var.vpc_cidr_c
  depends_on           = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_subnet" "d" {
  name                 = "subnet_d"
  resource_group_name  = azurerm_resource_group.CSIT.name
  virtual_network_name = azurerm_virtual_network.CSIT.name
  address_prefix       = var.vpc_cidr_d
  depends_on           = [ azurerm_resource_group.CSIT ]
}

# Create a security group of the Kiknos instances

resource "azurerm_network_security_group" "CSIT" {
  name                = "CSIT"
  resource_group_name = azurerm_resource_group.CSIT.name
  location            = azurerm_resource_group.CSIT.location
  security_rule {
    name                       = "IpSec"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Udp"
    source_port_range          = "*"
    destination_port_range     = "500"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "IpSec-NAT"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Udp"
    source_port_range          = "*"
    destination_port_range     = "4500"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "SSH"
    priority                   = 102
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "InboundAll"
    priority                   = 103
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "Outbound"
    priority                   = 104
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  depends_on = [azurerm_virtual_network.CSIT]
}

# Create public IPs

resource "azurerm_public_ip" "tg_public_ip" {
    name                         = "tg_public_ip"
    location                     = azurerm_resource_group.CSIT.location
    resource_group_name          = azurerm_resource_group.CSIT.name
    allocation_method            = "Dynamic"
    depends_on                   = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_public_ip" "dut1_public_ip" {
    name                         = "dut1_public_ip"
    location                     = azurerm_resource_group.CSIT.location
    resource_group_name          = azurerm_resource_group.CSIT.name
    allocation_method            = "Dynamic"
    depends_on                   = [ azurerm_resource_group.CSIT ]
}

resource "azurerm_public_ip" "dut2_public_ip" {
    name                         = "dut2_public_ip"
    location                     = azurerm_resource_group.CSIT.location
    resource_group_name          = azurerm_resource_group.CSIT.name
    allocation_method            = "Dynamic"
    depends_on                   = [ azurerm_resource_group.CSIT ]
}

# Create network interface

resource "azurerm_network_interface" "tg_mng" {
    name                      = "tg_mng"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    ip_configuration {
        primary                       = "true"
        name                          = "tg_mng_ip"
        subnet_id                     = azurerm_subnet.a.id
        private_ip_address_allocation = "Static"
        private_ip_address            = "172.16.0.10"
        public_ip_address_id          = azurerm_public_ip.tg_public_ip.id
    }
    depends_on                = [ azurerm_resource_group.CSIT,
                                  azurerm_subnet.a,
                                  azurerm_public_ip.tg_public_ip ]
}

resource "azurerm_network_interface" "dut1_mng" {
    name                      = "dut1_mng"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    ip_configuration {
        primary                       = "true"
        name                          = "dut1_mng_ip"
        subnet_id                     = azurerm_subnet.a.id
        private_ip_address_allocation = "Static"
        private_ip_address            = "172.16.0.11"
        public_ip_address_id          = azurerm_public_ip.dut1_public_ip.id
    }
    depends_on                = [ azurerm_resource_group.CSIT,
                                  azurerm_subnet.a,
                                  azurerm_public_ip.dut1_public_ip ]
}

resource "azurerm_network_interface" "dut2_mng" {
    name                      = "dut2_mng"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    ip_configuration {
        primary                       = "true"
        name                          = "dut2_mng_ip"
        subnet_id                     = azurerm_subnet.a.id
        private_ip_address_allocation = "Static"
        private_ip_address            = "172.16.0.12"
        public_ip_address_id          = azurerm_public_ip.dut2_public_ip.id
    }
    depends_on                = [ azurerm_resource_group.CSIT,
                                  azurerm_subnet.a,
                                  azurerm_public_ip.dut2_public_ip ]
}

resource "azurerm_route_table" "b" {
  name                          = "b"
  location                      = azurerm_resource_group.CSIT.location
  resource_group_name           = azurerm_resource_group.CSIT.name
  depends_on                    = [ azurerm_resource_group.CSIT,
                                    azurerm_subnet.b ]
  disable_bgp_route_propagation = false
  route {
    name                    = "route-10"
    address_prefix          = var.trex_dummy_cidr_port_0
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.tg_if1.private_ip_address
  }
  route {
    name                    = "route-20"
    address_prefix          = var.trex_dummy_cidr_port_1
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut1_if1.private_ip_address
  }
  route {
    name                    = "tg2"
    address_prefix          = var.vpc_cidr_d
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut1_if1.private_ip_address
  }
}

resource "azurerm_route_table" "c" {
  name                          = "c"
  location                      = azurerm_resource_group.CSIT.location
  resource_group_name           = azurerm_resource_group.CSIT.name
  depends_on                    = [ azurerm_resource_group.CSIT,
                                    azurerm_subnet.c ]
  disable_bgp_route_propagation = false
  route {
    name                    = "route-10"
    address_prefix          = var.trex_dummy_cidr_port_0
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut1_if2.private_ip_address
  }
  route {
    name                    = "route-100"
    address_prefix          = "100.0.0.0/8"
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut1_if2.private_ip_address
  }
  route {
    name                    = "route-20"
    address_prefix          = var.trex_dummy_cidr_port_1
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut2_if1.private_ip_address
  }
  route {
    name                    = "tg1"
    address_prefix          = var.vpc_cidr_b
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut1_if2.private_ip_address
  }
  route {
    name                    = "tg2"
    address_prefix          = var.vpc_cidr_d
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut2_if1.private_ip_address
  }
}

resource "azurerm_route_table" "d" {
  name                          = "d"
  location                      = azurerm_resource_group.CSIT.location
  resource_group_name           = azurerm_resource_group.CSIT.name
  depends_on                    = [ azurerm_resource_group.CSIT,
                                    azurerm_subnet.d ]
  disable_bgp_route_propagation = false
  route {
    name                    = "route-10"
    address_prefix          = var.trex_dummy_cidr_port_0
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut2_if2.private_ip_address
  }
  route {
    name                    = "route-20"
    address_prefix          = var.trex_dummy_cidr_port_1
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.tg_if2.private_ip_address
  }
  route {
    name                    = "tg1"
    address_prefix          = var.vpc_cidr_b
    next_hop_type           = "VirtualAppliance"
    next_hop_in_ip_address  = data.azurerm_network_interface.dut2_if2.private_ip_address
  }
}

resource "azurerm_subnet_route_table_association" "b" {
  subnet_id      = azurerm_subnet.b.id
  route_table_id = azurerm_route_table.b.id
}

resource "azurerm_subnet_route_table_association" "c" {
  subnet_id      = azurerm_subnet.c.id
  route_table_id = azurerm_route_table.c.id
}

resource "azurerm_subnet_route_table_association" "d" {
  subnet_id      = azurerm_subnet.d.id
  route_table_id = azurerm_route_table.d.id
}

resource "azurerm_virtual_machine" "tg" {
    name                             = "tg"
    location                         = azurerm_resource_group.CSIT.location
    resource_group_name              = azurerm_resource_group.CSIT.name
    primary_network_interface_id     = azurerm_network_interface.tg_mng.id
    network_interface_ids            = [ azurerm_network_interface.tg_mng.id,
                                         azurerm_network_interface.tg_if1.id,
                                         azurerm_network_interface.tg_if2.id ]
    vm_size                          = "Standard_F32s_v2"
    delete_os_disk_on_termination    = true
    delete_data_disks_on_termination = true
    storage_os_disk {
        name              = "OsDiskTG"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "StandardSSD_LRS"
    }
    storage_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }
    os_profile {
        computer_name  = "tg"
        admin_username = "ubuntu"
    }
    os_profile_linux_config {
        disable_password_authentication = true
        ssh_keys {
            path     = "/home/ubuntu/.ssh/authorized_keys"
            key_data = file("~/.ssh/id_rsa.pub")
        }
    }
    depends_on          = [ azurerm_resource_group.CSIT,
                            azurerm_network_interface.tg_mng ]
}

resource "azurerm_virtual_machine" "dut1" {
    name                             = "dut1"
    location                         = azurerm_resource_group.CSIT.location
    resource_group_name              = azurerm_resource_group.CSIT.name
    primary_network_interface_id     = azurerm_network_interface.dut1_mng.id
    network_interface_ids            = [ azurerm_network_interface.dut1_mng.id,
                                         azurerm_network_interface.dut1_if1.id,
                                         azurerm_network_interface.dut1_if2.id ]
    vm_size                          = "Standard_F32s_v2"
    delete_os_disk_on_termination    = true
    delete_data_disks_on_termination = true
    storage_os_disk {
        name              = "OsDiskDUT1"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "StandardSSD_LRS"
    }
    storage_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }
    os_profile {
        computer_name  = "dut1"
        admin_username = "ubuntu"
    }
    os_profile_linux_config {
        disable_password_authentication = true
        ssh_keys {
            path     = "/home/ubuntu/.ssh/authorized_keys"
            key_data = file("~/.ssh/id_rsa.pub")
        }
    }
    depends_on          = [ azurerm_resource_group.CSIT,
                            azurerm_network_interface.dut1_mng ]
}

resource "azurerm_virtual_machine" "dut2" {
    name                             = "dut2"
    location                         = azurerm_resource_group.CSIT.location
    resource_group_name              = azurerm_resource_group.CSIT.name
    primary_network_interface_id     = azurerm_network_interface.dut2_mng.id
    network_interface_ids            = [ azurerm_network_interface.dut2_mng.id,
                                         azurerm_network_interface.dut2_if1.id,
                                         azurerm_network_interface.dut2_if2.id ]
    vm_size                          = "Standard_F32s_v2"
    delete_os_disk_on_termination    = true
    delete_data_disks_on_termination = true
    storage_os_disk {
        name              = "OsDiskDUT2"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "StandardSSD_LRS"
    }
    storage_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }
    os_profile {
        computer_name  = "dut2"
        admin_username = "ubuntu"
    }
    os_profile_linux_config {
        disable_password_authentication = true
        ssh_keys {
            path     = "/home/ubuntu/.ssh/authorized_keys"
            key_data = file("~/.ssh/id_rsa.pub")
        }
    }
    depends_on          = [ azurerm_resource_group.CSIT,
                            azurerm_network_interface.dut2_mng ]
}

data "azurerm_public_ip" "tg_public_ip" {
  name                = "tg_public_ip"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.tg ]
}

data "azurerm_public_ip" "dut1_public_ip" {
  name                = "dut1_public_ip"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut1 ]
}

data "azurerm_public_ip" "dut2_public_ip" {
  name                = "dut2_public_ip"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut2 ]
}

# Provisioning

resource "null_resource" "deploy_tg" {
  depends_on = [ azurerm_virtual_machine.tg,
                 azurerm_network_interface.tg_if1,
                 azurerm_network_interface.tg_if2 ]
  connection {
    user = "ubuntu"
    host = data.azurerm_public_ip.tg_public_ip.ip_address
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../testbed-setup/ansible/site.yaml"
        force_handlers = true
      }
      hosts = ["tg_azure"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        azure = true
      }
    }
  }
}

resource "null_resource" "deploy_dut1" {
  depends_on = [ azurerm_virtual_machine.dut1,
                 azurerm_network_interface.dut1_if1,
                 azurerm_network_interface.dut1_if2 ]
  connection {
    user = "ubuntu"
    host = data.azurerm_public_ip.dut1_public_ip.ip_address
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../testbed-setup/ansible/site.yaml"
        force_handlers = true
      }
      hosts = ["sut_azure"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        azure = true
      }
    }
  }
}

resource "null_resource" "deploy_dut2" {
  depends_on = [ azurerm_virtual_machine.dut2,
                 azurerm_network_interface.dut2_if1,
                 azurerm_network_interface.dut2_if2 ]
  connection {
    user = "ubuntu"
    host = data.azurerm_public_ip.dut2_public_ip.ip_address
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../testbed-setup/ansible/site.yaml"
        force_handlers = true
      }
      hosts = ["sut_azure"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        azure = true
      }
    }
  }
}

resource "null_resource" "deploy_topology" {
  depends_on = [ azurerm_virtual_machine.tg,
                 azurerm_network_interface.tg_if1,
                 azurerm_network_interface.tg_if2,
                 azurerm_virtual_machine.dut1,
                 azurerm_network_interface.dut1_if1,
                 azurerm_network_interface.dut1_if2,
                 azurerm_virtual_machine.dut2,
                 azurerm_network_interface.dut2_if1,
                 azurerm_network_interface.dut2_if2 ]
  provisioner "ansible" {
    plays {
      playbook {
        file_path = "../../testbed-setup/ansible/cloud_topology.yaml"
      }
      hosts = ["local"]
      extra_vars = {
        ansible_python_interpreter = "/usr/bin/python3"
        cloud_topology = "3n_azure_Fsv2"
        tg_if1_mac = data.azurerm_network_interface.tg_if1.mac_address
        tg_if2_mac = data.azurerm_network_interface.tg_if2.mac_address
        dut1_if1_mac = data.azurerm_network_interface.dut1_if1.mac_address
        dut1_if2_mac = data.azurerm_network_interface.dut1_if2.mac_address
        dut2_if1_mac = data.azurerm_network_interface.dut2_if1.mac_address
        dut2_if2_mac = data.azurerm_network_interface.dut2_if2.mac_address
        tg_public_ip = data.azurerm_public_ip.tg_public_ip.ip_address
        dut1_public_ip = data.azurerm_public_ip.dut1_public_ip.ip_address
        dut2_public_ip = data.azurerm_public_ip.dut2_public_ip.ip_address
      }
    }
  }
}

output "dbg_tg" {
  value = "TG IP: ${data.azurerm_public_ip.tg_public_ip.ip_address}"
}

output "dbg_dut1" {
  value = "DUT1 IP: ${data.azurerm_public_ip.dut1_public_ip.ip_address}"
}

output "dbg_dut2" {
  value = "DUT2 IP: ${data.azurerm_public_ip.dut2_public_ip.ip_address}"
}
