locals {
  image_name       = "Ubuntu 22.04.2 LTS"
  image_source_url = "http://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
  resource_prefix  = "csit-2n"
  testbed_name     = "xu6n"
  topology_name    = "2n"
}

# Create Cloud-Init config for TG.
data "template_cloudinit_config" "cloudinit_config_tg1" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content = templatefile(
      "${path.module}/user-data-tg1", {}
    )
  }
}

# Create Cloud-Init config for SUT1.
data "template_cloudinit_config" "cloudinit_config_sut1" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content = templatefile(
      "${path.module}/user-data-sut1", {}
    )
  }
}

# Create OpenStack Image.
module "openstack_images_image_v2" {
  source  = "pmikus/images-image-v2/openstack"
  version = "1.54.1"

  image_source_url = local.image_source_url
  name             = local.image_name
}

# Create OpenStack Keypair.
module "openstack_compute_keypair_v2" {
  source  = "pmikus/compute-keypair-v2/openstack"
  version = "1.54.1"

  name = "${local.resource_prefix}-keypair"
}


# Create management port in dedicated subnet.
resource "openstack_networking_port_v2" "port_tg1_mgmt" {
  admin_state_up = true
  fixed_ip {
    ip_address = "10.21.152.2"
    subnet_id  = "b1f9573d-4c2e-45da-bbac-cb3f191ab0f5"
  }
  name                  = "${local.resource_prefix}-tg1-mgmt-port"
  network_id            = var.network_id_mgmt
  port_security_enabled = false

  binding {
    vnic_type = "normal"
  }
}

# Create data port in dedicated subnet.
resource "openstack_networking_port_v2" "port_tg1_data1" {
  admin_state_up        = false
  name                  = "${local.resource_prefix}-tg1-data1-port"
  network_id            = var.network_id_data
  port_security_enabled = false

  binding {
    vnic_type = "direct"
  }
}

# Create data port in dedicated subnet.
resource "openstack_networking_port_v2" "port_tg1_data2" {
  admin_state_up        = false
  name                  = "${local.resource_prefix}-tg1-data2-port"
  network_id            = var.network_id_data
  port_security_enabled = false

  binding {
    vnic_type = "direct"
  }
}

# Create TG instance.
module "tg1" {
  depends_on = [
    module.openstack_compute_keypair_v2,
    module.openstack_images_image_v2
  ]

  source  = "pmikus/compute-instance-v2/openstack"
  version = "1.54.1"

  flavour_name = var.flavour_name
  image_id     = module.openstack_images_image_v2.id
  key_pair     = module.openstack_compute_keypair_v2.name
  name         = "${local.resource_prefix}-tg1"
  networks = {
    "platform-shared-port"  = openstack_networking_port_v2.port_tg1_mgmt.id
    "data-playground-port1" = openstack_networking_port_v2.port_tg1_data1.id
    "data-playground-port2" = openstack_networking_port_v2.port_tg1_data2.id
  }
  user_data = data.template_cloudinit_config.cloudinit_config_tg1.rendered
}

# Create management port in dedicated subnet.
resource "openstack_networking_port_v2" "port_sut1_mgmt" {
  admin_state_up = true
  fixed_ip {
    ip_address = "10.21.152.3"
    subnet_id  = "b1f9573d-4c2e-45da-bbac-cb3f191ab0f5"
  }
  name                  = "${local.resource_prefix}-sut1-mgmt-port"
  network_id            = var.network_id_mgmt
  port_security_enabled = false

  binding {
    vnic_type = "normal"
  }
}

# Create data port in dedicated subnet.
resource "openstack_networking_port_v2" "port_sut1_data1" {
  admin_state_up        = false
  name                  = "${local.resource_prefix}-sut1-data1-port"
  network_id            = var.network_id_data
  port_security_enabled = false

  binding {
    vnic_type = "direct"
  }
}

# Create data port in dedicated subnet.
resource "openstack_networking_port_v2" "port_sut1_data2" {
  admin_state_up        = false
  name                  = "${local.resource_prefix}-sut1-data2-port"
  network_id            = var.network_id_data
  port_security_enabled = false

  binding {
    vnic_type = "direct"
  }
}

# Create SUT instance.
module "sut1" {
  depends_on = [
    module.openstack_compute_keypair_v2,
    module.openstack_images_image_v2
  ]

  source  = "pmikus/compute-instance-v2/openstack"
  version = "1.54.1"

  flavour_name = var.flavour_name
  image_id     = module.openstack_images_image_v2.id
  key_pair     = module.openstack_compute_keypair_v2.name
  name         = "${local.resource_prefix}-sut1"
  networks = {
    "platform-shared-port"  = openstack_networking_port_v2.port_sut1_mgmt.id
    "data-playground-port1" = openstack_networking_port_v2.port_sut1_data1.id
    "data-playground-port2" = openstack_networking_port_v2.port_sut1_data2.id
  }
  user_data = data.template_cloudinit_config.cloudinit_config_sut1.rendered
}

resource "local_file" "topology_file" {
  depends_on = [
    module.tg1,
    module.sut1
  ]

  content = templatefile(
    "${path.module}/topology-${local.topology_name}.tftpl",
    {
      tg_if1_mac     = openstack_networking_port_v2.port_tg1_data1.mac_address
      tg_if2_mac     = openstack_networking_port_v2.port_tg1_data2.mac_address
      dut1_if1_mac   = openstack_networking_port_v2.port_sut1_data1.mac_address
      dut1_if2_mac   = openstack_networking_port_v2.port_sut1_data2.mac_address
      tg_public_ip   = openstack_networking_port_v2.port_tg1_mgmt.fixed_ip[0].ip_address
      dut1_public_ip = openstack_networking_port_v2.port_sut1_mgmt.fixed_ip[0].ip_address
    }
  )
  filename = "${path.module}/${local.topology_name}-x-${local.testbed_name}.yaml"
}

resource "local_file" "hosts" {
  depends_on = [
    module.tg1,
    module.sut1
  ]

  content = templatefile(
    "${path.module}/hosts.tftpl",
    {
      tg_public_ip   = openstack_networking_port_v2.port_tg1_mgmt.fixed_ip[0].ip_address
      dut1_public_ip = openstack_networking_port_v2.port_sut1_mgmt.fixed_ip[0].ip_address
    }
  )
  filename = "${path.module}/hosts.yaml"
}
