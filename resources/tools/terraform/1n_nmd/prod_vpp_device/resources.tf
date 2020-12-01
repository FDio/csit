resource "nomad_job" "prod_csit_shim_arm" {
  provider = nomad
  jobspec  = file("${path.module}/prod_csit_shim_arm.nomad")
}

resource "nomad_job" "prod_csit_shim_amd" {
  provider = nomad
  jobspec  = file("${path.module}/prod_csit_shim_amd.nomad")
}