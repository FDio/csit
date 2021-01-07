output "minio_service_name" {
  description = "Minio service name"
  value       = data.template_file.nomad_job_minio.vars.service_name
}