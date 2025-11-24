resource "nomad_job" "nomad_job" {
  for_each = { for job in var.nomad_jobs : job.job_name => job }
  jobspec = file("${path.cwd}/conf/nomad/${each.key}.hcl")
  hcl2 {
    vars = {
        cron   = "0 30 0 * * * *"
        memory = each.value.memory,
        script_name = each.value.script_name,
    }
  }
  detach = false
}