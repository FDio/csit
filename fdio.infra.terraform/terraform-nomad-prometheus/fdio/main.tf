module "prometheus" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  # prometheus
  datacenters = ["yul1"]
  pm_version  = "2.33.1"
}