module "vpp-device" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  # nomad
  datacenters   = ["yul1"]
  job_name      = "device-shim"
  group_count   = 1
  cpu           = 1500
  memory        = 4096
  image_aarch64 = "fdiotools/csit_shim-ubuntu2004:2021_03_02_143938_UTC-aarch64"
  image_x86_64  = "fdiotools/csit_shim-ubuntu2004:2021_03_04_142103_UTC-x86_64"
}

