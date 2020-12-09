locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_nginx" {
  template    = file("${path.module}/conf/nomad/nginx.hcl")
  vars        = {
    job_name    = var.nginx_job_name
    datacenters = local.datacenters
  }
}

resource "nomad_job" "nomad_job_nginx" {
  jobspec     = data.template_file.nomad_job_nginx.rendered
  detach      = false
}