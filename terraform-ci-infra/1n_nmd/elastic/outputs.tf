output "beats_service_name" {
  description = "Beats service name"
  value       = data.template_file.nomad_job_beats.vars.service_name
}

output "beats_port" {
  description = "Beats port number"
  value       = data.template_file.nomad_job_beats.vars.port
}
