# For convenience in simple configurations, a child module automatically
# inherits default (un-aliased) provider configurations from its parent.
# This means that explicit provider blocks appear only in the root module,
# and downstream modules can simply declare resources for that provider
# and have them automatically associated with the root provider
# configurations.
module "alertmanager" {
  source                             = "./alertmanager"
  providers                          = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters                  = [ "yul1" ]

  # alertmanager
  alertmanager_job_name              = "prod-alertmanager"
  alertmanager_use_canary            = true
  alertmanager_group_count           = 1
  alertmanager_vault_secret          = {
    use_vault_provider               = false,
    vault_kv_policy_name             = "kv-secret",
    vault_kv_path                    = "secret/data/prometheus",
    vault_kv_field_access_key        = "access_key",
    vault_kv_field_secret_key        = "secret_key"
  }
  alertmanager_version               = "0.21.0"
  alertmanager_cpu                   = 1000
  alertmanager_mem                   = 1024
  alertmanager_port                  = 9093
  alertmanager_slack_jenkins_api_key = "TE07RD1V1/B01LPL8KM0F/KAd80wc9vS8CPMtrNtmQqCfT"
  alertmanager_slack_jenkins_channel = "fdio-jobs-monitoring"
  alertmanager_slack_default_api_key = "TE07RD1V1/B01L7PQK9S8/hkn7cWKiARfh1H0ppC5aYtbr"
  alertmanager_slack_default_channel = "fdio-infra-monitoring"
}

module "grafana" {
  source                         = "./grafana"
  providers                      = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters              = [ "yul1" ]

  # grafana
  grafana_job_name               = "prod-grafana"
  grafana_use_canary             = true
  grafana_group_count            = 1
  grafana_vault_secret           = {
    use_vault_provider           = false,
    vault_kv_policy_name         = "kv-secret",
    vault_kv_path                = "secret/data/grafana",
    vault_kv_field_access_key    = "access_key",
    vault_kv_field_secret_key    = "secret_key"
  }
  grafana_container_image        = "grafana/grafana:7.3.7"
  grafana_cpu                    = 1000
  grafana_mem                    = 2048
  grafana_port                   = 3000
}

module "minio" {
  source                         = "./minio"
  providers                      = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters              = [ "yul1" ]
  nomad_host_volume              = "prod-volume-data1-1"

  # minio
  minio_job_name                 = "prod-minio"
  minio_group_count              = 4
  minio_service_name             = "storage"
  minio_host                     = "http://10.32.8.1{4...7}"
  minio_port                     = 9000
  minio_container_image          = "minio/minio:RELEASE.2020-12-03T05-49-24Z"
  minio_vault_secret             = {
    use_vault_provider           = false,
    vault_kv_policy_name         = "kv-secret",
    vault_kv_path                = "secret/data/minio",
    vault_kv_field_access_key    = "access_key",
    vault_kv_field_secret_key    = "secret_key"
  }
  minio_data_dir                 = "/data/"
  minio_use_host_volume          = true
  minio_use_canary               = true
  minio_envs                     = [ "MINIO_BROWSER=\"off\"" ]

  # minio client
  mc_job_name                    = "prod-mc"
  mc_container_image             = "minio/mc:RELEASE.2020-12-10T01-26-17Z"
  mc_extra_commands              = [
    "mc policy set public LOCALMINIO/logs.fd.io",
    "mc policy set public LOCALMINIO/docs.fd.io",
    "mc ilm add --expiry-days '180' LOCALMINIO/logs.fd.io",
    "mc admin user add LOCALMINIO storage Storage1234",
    "mc admin policy set LOCALMINIO writeonly user=storage"
  ]
  minio_buckets                  = [ "logs.fd.io", "docs.fd.io" ]
}

module "nginx" {
  source                         = "./nginx"
  providers                      = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters              = [ "yul1" ]

  # nginx
  nginx_job_name                 = "prod-nginx"
}

module "prometheus" {
  source                         = "./prometheus"
  providers                      = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters              = [ "yul1" ]
  nomad_host_volume              = "prod-volume-data1-1"

  # prometheus
  prometheus_job_name            = "prod-prometheus"
  prometheus_use_canary          = true
  prometheus_group_count         = 4
  prometheus_vault_secret        = {
    use_vault_provider           = false,
    vault_kv_policy_name         = "kv-secret",
    vault_kv_path                = "secret/data/prometheus",
    vault_kv_field_access_key    = "access_key",
    vault_kv_field_secret_key    = "secret_key"
  }
  prometheus_data_dir            = "/data/"
  prometheus_use_host_volume     = true
  prometheus_version             = "2.24.0"
  prometheus_cpu                 = 2000
  prometheus_mem                 = 8192
  prometheus_port                = 9090
}

module "vpp_device" {
  source                         = "./vpp_device"
  providers                      = {
    nomad = nomad.yul1
  }

  # nomad
  nomad_datacenters              = [ "yul1" ]

  # csit_shim
  csit_shim_job_name             = "prod-device-csit-shim"
  csit_shim_group_count          = "1"
  csit_shim_cpu                  = "1500"
  csit_shim_mem                  = "4096"
  csit_shim_image_aarch64        = "fdiotools/csit_shim-ubuntu2004:2021_02_26_075614-aarch64"
  csit_shim_image_x86_64         = "fdiotools/csit_shim-ubuntu2004:2021_02_26_081228-x86_64"
}