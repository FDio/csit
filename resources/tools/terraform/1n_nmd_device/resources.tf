resource "nomad_job" "prod-csit-arm" {
  provider = nomad.yul1
  jobspec  = file("${path.module}/prod-csit-arm.nomad")
}

resource "nomad_job" "prod-csit-amd" {
  provider = nomad.yul1
  jobspec  = file("${path.module}/prod-csit-amd.nomad")
}