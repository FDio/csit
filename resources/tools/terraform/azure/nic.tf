# Create a network interface for the data-plane traffic

resource "azurerm_network_interface" "dut1_if2" {
    name                      = "dut1_if2"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "dut1_if2"
        subnet_id                     = azurerm_subnet.c.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.200.101"
    }
}

data "azurerm_network_interface" "dut1_if2" {
  name                = "dut1_if2"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut1 ]
}

resource "azurerm_network_interface" "dut2_if1" {
    name                      = "dut2_if1"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "dut2_if1"
        subnet_id                     = azurerm_subnet.c.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.200.102"
    }
}

data "azurerm_network_interface" "dut2_if1" {
  name                = "dut2_if1"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut2 ]
}

resource "azurerm_network_interface" "dut1_if1" {
    name                      = "dut1_if1"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "dut1_if1"
        subnet_id                     = azurerm_subnet.b.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.10.11"
    }
}

data "azurerm_network_interface" "dut1_if1" {
  name                = "dut1_if1"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut1 ]
}

resource "azurerm_network_interface" "dut2_if2" {
    name                      = "dut2_if2"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "dut2_if2"
        subnet_id                     = azurerm_subnet.d.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.20.11"
    }
}

data "azurerm_network_interface" "dut2_if2" {
  name                = "dut2_if2"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.dut2 ]
}

resource "azurerm_network_interface" "tg_if1" {
    name                      = "tg_if1"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "tg1"
        subnet_id                     = azurerm_subnet.b.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.10.250"
    }
}

data "azurerm_network_interface" "tg_if1" {
  name                = "tg_if1"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.tg ]
}

resource "azurerm_network_interface" "tg_if2" {
    name                      = "tg_if2"
    location                  = azurerm_resource_group.CSIT.location
    resource_group_name       = azurerm_resource_group.CSIT.name
    network_security_group_id = azurerm_network_security_group.CSIT.id
    enable_ip_forwarding      = "true"
    enable_accelerated_networking  = "true"

    ip_configuration {
        name                          = "tg2"
        subnet_id                     = azurerm_subnet.d.id
        private_ip_address_allocation = "Static"
        private_ip_address	      = "172.16.20.250"
    }
}

data "azurerm_network_interface" "tg_if2" {
  name                = "tg_if2"
  resource_group_name = azurerm_resource_group.CSIT.name
  depends_on          = [ azurerm_virtual_machine.tg ]
}
