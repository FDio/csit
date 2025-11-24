variable "datacenter" {
  # Set the `NOMAD_VAR_datacenter` environment variable to override the
  # default for the task.
  type    = string
  default = "yul1"
}

variable "namespace" {
  # Set the `NOMAD_VAR_namespace` environment variable to override the
  # default for the task.
  type    = string
  default = "etl"
}

variable "cron" {
  type = string
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
  default = 10000
}

variable "image" {
  # Set the `NOMAD_VAR_image` environment variable to override the
  # default for the task.
  type    = string
  default = "pmikus/docker-ubuntu-focal-aws-glue:latest"
}

variable "memory" {
  # Set the `NOMAD_VAR_memory` environment variable to override the
  # default for the task.
  type    = number
  default = 24000
}

variable "script_name" {
  # Set the `NOMAD_VAR_script_name` environment variable to override the
  # default for the task.
  type    = string
  default = "local"
}

job "etl-trending-ndrpdr" {
  datacenters = [var.datacenter]
  type        = "batch"
  namespace   = var.namespace

  periodic {
    cron             = var.cron
    prohibit_overlap = true
    time_zone        = "UTC"
  }

  group "etl-trending-ndrpdr" {
    restart {
      mode = "fail"
    }
    constraint {
      attribute = "$${attr.cpu.arch}"
      value     = var.constraint_arch
    }
    constraint {
      attribute = "$${node.class}"
      value     = var.constraint_class
    }
    task "etl-trending-ndrpdr" {
      artifact {
        source      = "https://raw.githubusercontent.com/FDio/csit/master/csit.infra.etl/${var.script_name}.py"
        destination = "local/"
      }
      artifact {
        source      = "https://raw.githubusercontent.com/FDio/csit/master/csit.infra.etl/${var.script_name}.json"
        destination = "local/"
      }
      driver = "docker"
      config {
        image   = var.image
        command = "gluesparksubmit"
        args = [
          "--driver-memory", "30g",
          "--executor-memory", "30g",
          "--executor-cores", "2",
          "--master", "local[2]",
          "${var.script_name}.py"
        ]
        work_dir = "/local"
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
    }
  }
}
