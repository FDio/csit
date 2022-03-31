# For convenience in simple configurations, a child module automatically
# inherits default (un-aliased) provider configurations from its parent.
# This means that explicit provider blocks appear only in the root module,
# and downstream modules can simply declare resources for that provider
# and have them automatically associated with the root provider
# configurations.

#module "minio" {
#  source = "./minio"
#  providers = {
#    nomad = nomad.yul1
#  }
#
#  # nomad
#  nomad_datacenters = ["yul1"]
#  nomad_host_volume = "prod-volume-data1-1"
#
#  # minio
#  minio_job_name        = "prod-minio"
#  minio_group_count     = 4
#  minio_service_name    = "storage"
#  minio_host            = "http://10.32.8.1{4...7}"
#  minio_port            = 9000
#  minio_container_image = "minio/minio:RELEASE.2021-07-27T02-40-15Z"
#  minio_vault_secret = {
#    use_vault_provider        = false,
#    vault_kv_policy_name      = "kv-secret",
#    vault_kv_path             = "secret/data/minio",
#    vault_kv_field_access_key = "access_key",
#    vault_kv_field_secret_key = "secret_key"
#  }
#  minio_data_dir        = "/data/"
#  minio_use_host_volume = true
#  minio_use_canary      = true
#  minio_envs            = ["MINIO_BROWSER=\"off\""]
#
#  minio_buckets = ["logs.fd.io"]
#}

data "vault_generic_secret" "minio_creds" {
  path = "kv/secret/data/minio"
}

#module "nginx" {
#  source = "./nginx"
#  providers = {
#    nomad = nomad.yul1
#  }
#
#  # nomad
#  nomad_datacenters = ["yul1"]
#  nomad_host_volume = "prod-volume-data1-1"
#
#  # nginx
#  nginx_job_name        = "prod-nginx"
#  nginx_use_host_volume = true
#}

module "vpp_device" {
  source = "./vpp_device"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters = ["yul1"]

  # csit_shim
  csit_shim_job_name      = "prod-device-csit-shim"
  csit_shim_group_count   = "1"
  csit_shim_cpu           = "1500"
  csit_shim_mem           = "4096"
  csit_shim_image_aarch64 = "fdiotools/csit_shim-ubuntu2004:2021_03_02_143938_UTC-aarch64"
  csit_shim_image_x86_64  = "fdiotools/csit_shim-ubuntu2004:2021_03_04_142103_UTC-x86_64"
}
