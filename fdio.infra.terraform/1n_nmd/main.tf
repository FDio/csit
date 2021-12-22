# For convenience in simple configurations, a child module automatically
# inherits default (un-aliased) provider configurations from its parent.
# This means that explicit provider blocks appear only in the root module,
# and downstream modules can simply declare resources for that provider
# and have them automatically associated with the root provider
# configurations.
data "vault_generic_secret" "minio_creds" {
  path = "kv/secret/data/minio"
}

module "alertmanager" {
  source = "./alertmanager"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters = ["yul1"]

  # alertmanager
  alertmanager_job_name    = "prod-alertmanager"
  alertmanager_use_canary  = true
  alertmanager_group_count = 1
  alertmanager_vault_secret = {
    use_vault_provider        = false,
    vault_kv_policy_name      = "kv-secret",
    vault_kv_path             = "secret/data/prometheus",
    vault_kv_field_access_key = "access_key",
    vault_kv_field_secret_key = "secret_key"
  }
  alertmanager_version               = "0.21.0"
  alertmanager_cpu                   = 1000
  alertmanager_mem                   = 1024
  alertmanager_port                  = 9093
  alertmanager_slack_jenkins_api_key = "TE07RD1V1/B01U1NV9HV3/hKZXJJ74g2JcISq4K3QC1eG9"
  alertmanager_slack_jenkins_channel = "fdio-jobs-monitoring"
  alertmanager_slack_default_api_key = "TE07RD1V1/B01UUK23B6C/hZTcCu42FUv8d6rtirHtcYIi"
  alertmanager_slack_default_channel = "fdio-infra-monitoring"
}

module "grafana" {
  source = "./grafana"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters = ["yul1"]

  # grafana
  grafana_job_name    = "prod-grafana"
  grafana_use_canary  = true
  grafana_group_count = 1
  grafana_vault_secret = {
    use_vault_provider        = false,
    vault_kv_policy_name      = "kv-secret",
    vault_kv_path             = "secret/data/grafana",
    vault_kv_field_access_key = "access_key",
    vault_kv_field_secret_key = "secret_key"
  }
  grafana_container_image = "grafana/grafana:7.3.7"
  grafana_cpu             = 1000
  grafana_mem             = 2048
  grafana_port            = 3000
}

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

module "minio_s3_gateway" {
  source = "./minio_s3_gateway"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  datacenters   = ["yul1"]
  volume_source = "prod-volume-data1-1"

  # minio
  job_name           = "minio-s3-gateway"
  group_count        = 4
  service_name       = "minio"
  mode               = "gateway"
  port_base          = 9001
  port_console       = 9002
  image              = "minio/minio:latest"
  access_key         = data.vault_generic_secret.minio_creds.data["access_key"]
  secret_key         = data.vault_generic_secret.minio_creds.data["secret_key"]
  volume_destination = "/data/"
  use_host_volume    = true
  use_canary         = true
  envs = [
    "MINIO_BROWSER=\"off\"",
    "MINIO_CACHE=\"on\"",
    "MINIO_CACHE_DRIVES=\"/data/s3_cache1\"",
    "MINIO_CACHE_EXCLUDE=\"\"",
    "MINIO_CACHE_QUOTA=80",
    "MINIO_CACHE_AFTER=1",
    "MINIO_CACHE_WATERMARK_LOW=70",
    "MINIO_CACHE_WATERMARK_HIGH=90"
  ]
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

module "prometheus" {
  source = "./prometheus"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters = ["yul1"]
  nomad_host_volume = "prod-volume-data1-1"

  # prometheus
  prometheus_job_name    = "prod-prometheus"
  prometheus_use_canary  = true
  prometheus_group_count = 4
  prometheus_vault_secret = {
    use_vault_provider        = false,
    vault_kv_policy_name      = "kv-secret",
    vault_kv_path             = "secret/data/prometheus",
    vault_kv_field_access_key = "access_key",
    vault_kv_field_secret_key = "secret_key"
  }
  prometheus_data_dir        = "/data/"
  prometheus_use_host_volume = true
  prometheus_version         = "2.28.1"
  prometheus_cpu             = 2000
  prometheus_mem             = 8192
  prometheus_port            = 9090
}

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
