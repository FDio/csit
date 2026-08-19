resource "nomad_job" "nomad_job" {
  jobspec = file("${path.cwd}/conf/nomad/alertmanager.hcl")
  hcl2 {
    vars = {
        version = "0.34.0"
    }
  }
  detach = false
}