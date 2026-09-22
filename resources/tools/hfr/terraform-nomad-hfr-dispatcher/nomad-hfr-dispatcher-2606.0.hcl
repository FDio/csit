variable "datacenters" {
  # Set the `NOMAD_VAR_datacenter` environment variable to override the
  # default for the task.
  type    = string
  default = "yul1"
}

variable "namespace" {
  # Set the `NOMAD_VAR_namespace` environment variable to override the
  # default for the task.
  type    = string
  default = "hfr"
}

variable "constraint_arch" {
  # Set the `NOMAD_VAR_constraint_arch` environment variable to override the
  # default for the task.
  type    = string
  default = "amd64"
}

variable "constraint_class" {
  # Set the `NOMAD_VAR_constraint_class` environment variable to override the
  # default for the task.
  type    = string
  default = "builder"
}

variable "cpu" {
  # Set the `NOMAD_VAR_cpu` environment variable to override the
  # default for the task.
  type    = number
}

variable "image" {
  # Set the `NOMAD_VAR_image` environment variable to override the
  # default for the task.
  type    = string
}

variable "job_name" {
  # Set the `NOMAD_VAR_job_name` environment variable to override the
  # default for the task.
  type    = string
}

variable "memory" {
  # Set the `NOMAD_VAR_memory` environment variable to override the
  # default for the task.
  type    = number
}

variable "use_host_volume" {
  # Set the `NOMAD_VAR_use_host_volume` environment variable to override the
  # default for the task.
  description = "Use Nomad host volume feature"
  type    = bool
  default = true
}

variable "volume_destination" {
  # Set the `NOMAD_VAR_volume_destination` environment variable to override the
  # default for the task.
  description = "Specifies where the volume should be mounted inside the task"
  type        = string
  default     = "/data/"
}

job "hfr-2606.0" {
  name        = var.job_name
  datacenters = [var.datacenters]
  type        = "batch"
  region      = "global"
  namespace   = var.namespace
  node_pool   = "default"

  group "hfr-2606.0" {
    count = 1
    constraint {
      attribute = "$${attr.cpu.arch}"
      value     = var.constraint_arch
    }
    constraint {
      attribute = "$${node.class}"
      value     = var.constraint_class
    }
    ephemeral_disk {
      migrate = false
      size    = 3000
      sticky  = false
    }
    restart {
      attempts = 0
      mode     = "fail"
    }
    volume "hfr-master-volume-1" {
      type      = "host"
      read_only = false
      source    = var.volume_source
    }
    task "hfr-2606.0" {
      driver = "docker"
      config {
        force_pull = true
        image = var.image
      }
      template {
        destination = "${NOMAD_SECRETS_DIR}/.env"
        env         = true
        data        = <<EOT
{{- with nomadVar "nomad/jobs" -}}
{{- range $k, $v := . }}
{{ $k }}={{ $v }}
{{- end }}
{{- end }}
EOT
      }
      resources {
        cpu    = var.cpu
        memory = var.memory
      }
      volume_mount {
        volume      = "hfr-master-volume-1"
        destination = var.volume_destination
        read_only   = false
      }
    }
  }
}