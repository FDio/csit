resource "nomad_job" "prod-csit-arm" {
  provider = nomad
  jobspec  = file("${path.module}/prod-csit-arm.nomad")
}

resource "nomad_job" "prod-csit-amd" {
  provider = nomad
  jobspec  = file("${path.module}/prod-csit-amd.nomad")
}