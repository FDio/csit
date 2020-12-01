terraform {
  # This module is now only being tested with Terraform 0.13.x.
  required_version = ">= 0.13"
}

provider "nomad" {
  address = var.nomad_provider_address
  alias   = "yul1"
}

# For convenience in simple configurations, a child module automatically
# inherits default (un-aliased) provider configurations from its parent.
# This means that explicit provider blocks appear only in the root module,
# and downstream modules can simply declare resources for that provider
# and have them automatically associated with the root provider
# configurations.

# prod_storage
#   + docs.nginx.service.consul
#   + logs.nginx.service.consul
#   + storage.nginx.service.consul
module "prod_storage" {
  source = "./prod_storage"
  providers = {
    nomad = nomad.yul1
  }
}

# prod_vpp_device
#   + csitarm
#   + csitamd
module "prod_vpp_device" {
  source = "./prod_vpp_device"
  providers = {
    nomad = nomad.yul1
  }
}
