output "minio_service_name" {
  description = "Minio service name"
  value       = data.template_file.nomad_job_minio.vars.service_name
<<<<<<< HEAD   (673b20 Infra: Terraform vpp_device module)
}

output "minio_access_key" {
  description = "Minio access key"
  value       = data.template_file.nomad_job_minio.vars.access_key
  sensitive   = true
}

output "minio_secret_key" {
  description = "Minio secret key"
  value       = data.template_file.nomad_job_minio.vars.secret_key
  sensitive   = true
}

output "minio_port" {
  description = "Minio port number"
  value = data.template_file.nomad_job_minio.vars.port
}
=======
}
>>>>>>> CHANGE (95a7a5 Infra: Remove unwanted terraform output)
