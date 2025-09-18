locals {
  datacenters = join(",", var.datacenters)
}

resource "nomad_job" "gha-dispatcher" {
  for_each = toset(var.namespace)
  jobspec = templatefile(
    "${path.cwd}/nomad-${var.job_name}-${each.key}.hcl.tftpl",
    {
      cpu         = var.cpu,
      datacenters = local.datacenters,
      image       = "${var.image}-${each.key}:latest",
      job_name    = "${var.job_name}-${each.key}",
      memory      = var.memory,
      namespace   = each.key,
      node_pool   = var.node_pool,
      region      = var.region,
      type        = var.type
  })
  detach = false
}