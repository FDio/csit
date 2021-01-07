output "prometheus_service_name" {
  description = "Prometheus service name"
  value       = data.template_file.nomad_job_prometheus.vars.prometheus_service_name
}