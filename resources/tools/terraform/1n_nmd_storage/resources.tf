resource "nomad_job" "prod_nginx" {
  provider = nomad.yul1
  jobspec  = file("${path.module}/prod-nginx.nomad")
}

resource "nomad_job" "prod_storage" {
  provider = nomad.yul1
  jobspec  = file("${path.module}/prod-storage.nomad")
}