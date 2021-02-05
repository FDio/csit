locals {
  datacenters      = join(",", var.nomad_datacenters)

  alertmanager_url = join("",
    [
      "https://github.com",
      "/prometheus/alertmanager/releases/download/",
      "v${var.alertmanager_version}/",
      "alertmanager-${var.alertmanager_version}.linux-amd64.tar.gz"
    ]
  )
}

data "template_file" "nomad_job_alertmanager" {
  template         = file("${path.module}/conf/nomad/alertmanager.hcl")
  vars             = {
    datacenters            = local.datacenters
    url                    = local.alertmanager_url
    job_name               = var.alertmanager_job_name
    use_canary             = var.alertmanager_use_canary
    group_count            = var.alertmanager_group_count
    service_name           = var.alertmanager_service_name
    use_vault_provider     = var.alertmanager_vault_secret.use_vault_provider
    version                = var.alertmanager_version
    cpu                    = var.alertmanager_cpu
    mem                    = var.alertmanager_mem
    port                   = var.alertmanager_port
    slack_jenkins_api_key  = var.alertmanager_slack_jenkins_api_key
    slack_jenkins_channel  = var.alertmanager_slack_jenkins_channel
    slack_jenkins_receiver = var.alertmanager_slack_jenkins_receiver
    slack_default_api_key  = var.alertmanager_slack_default_api_key
    slack_default_channel  = var.alertmanager_slack_default_channel
    slack_default_receiver = var.alertmanager_slack_default_receiver
  }
}

resource "nomad_job" "nomad_job_alertmanager" {
  jobspec          = data.template_file.nomad_job_alertmanager.rendered
  detach           = false
}