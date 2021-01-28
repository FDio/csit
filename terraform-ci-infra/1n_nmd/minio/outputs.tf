<<<<<<< HEAD   (7c90b6 Infra: Terraform vpp_device module)
=======
output "minio_service_name" {
  description = "Minio service name"
  value       = data.template_file.nomad_job_minio.vars.service_name
}
>>>>>>> CHANGE (6cc623 Infra: Remove unwanted terraform output)
