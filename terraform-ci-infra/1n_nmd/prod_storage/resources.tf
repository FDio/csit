resource "nomad_job" "prod_nginx" {
  provider = nomad
  jobspec  = file("${path.module}/prod-nginx.nomad")
}

resource "nomad_job" "prod_storage" {
  provider = nomad
  jobspec  = file("${path.module}/prod-storage.nomad")
}