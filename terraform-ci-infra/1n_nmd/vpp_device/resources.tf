resource "nomad_job" "prod_csit_shim" {
  provider = nomad
  jobspec  = file("${path.module}/prod_csit_shim.nomad")
}