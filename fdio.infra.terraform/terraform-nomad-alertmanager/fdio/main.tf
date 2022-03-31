module "alertmanager" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  # alertmanager
  datacenters           = ["yul1"]
  slack_jenkins_api_key = "TE07RD1V1/B01U1NV9HV3/hKZXJJ74g2JcISq4K3QC1eG9"
  slack_jenkins_channel = "fdio-jobs-monitoring"
  slack_default_api_key = "TE07RD1V1/B01UUK23B6C/hZTcCu42FUv8d6rtirHtcYIi"
  slack_default_channel = "fdio-infra-monitoring"
  am_version            = "0.23.0"
}