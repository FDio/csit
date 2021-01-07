output "elastic_service_name" {
  description = "Elastic service name"
  value       = data.template_file.nomad_job_elastic.vars.service_name
}