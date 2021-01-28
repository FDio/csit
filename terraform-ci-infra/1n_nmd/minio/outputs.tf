<<<<<<< HEAD   (7a760c Infra: Terraform vpp_device module)
=======
output "minio_service_name" {
  description = "Minio service name"
  value       = data.template_file.nomad_job_minio.vars.service_name
}
>>>>>>> CHANGE (d5b591 Infra: Remove unwanted terraform output)
