resource "nomad_job" "nomad_job" {
  jobspec = file("${path.cwd}/conf/nomad/prometheus.hcl")
  hcl2 {
    vars = {
        version = "3.14.0"
    }
  }
  detach = false
}