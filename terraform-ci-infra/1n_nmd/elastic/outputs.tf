output "elastic_cluster_service_name" {
  description = "Elastic cluster service name"
  value       = data.template_file.nomad_job_elastic.vars.cluster_service_name
}

output "elastic_kibana_service_name" {
  description = "Elastic kibana service name"
  value       = data.template_file.nomad_job_elastic.vars.kibana_service_name
}