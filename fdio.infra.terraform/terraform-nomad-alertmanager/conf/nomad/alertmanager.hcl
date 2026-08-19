variable "datacenter" {
  # Set the `NOMAD_VAR_datacenter` environment variable to override the
  # default for the task.
  type    = string
  default = "yul1"
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
  default = 1000
}

variable "version" {
  # Set the `NOMAD_VAR_version` environment variable to override the
  # default for the task.
  type    = string
  default = "0.34.0"
}

variable "memory" {
  # Set the `NOMAD_VAR_memory` environment variable to override the
  # default for the task.
  type    = number
  default = 1024
}

job "alertmanager" {
  datacenters = [var.datacenter]
  type        = "service"

  update {
    max_parallel      = 1
    health_check      = "checks"
    min_healthy_time  = "10s"
    healthy_deadline  = "3m"
    progress_deadline = "10m"
    canary            = 1
    auto_promote      = true
    auto_revert       = true
  }
  constraint {
    operator = "distinct_hosts"
    value    = "true"
  }

  group "alertmanager" {
    count = 1
    restart {
      interval = "30m"
      attempts = 40
      delay    = "15s"
      mode     = "delay"
    }
    constraint {
      attribute = "$${attr.cpu.arch}"
      value     = var.constraint_arch
    }
    constraint {
      attribute = "$${node.class}"
      value     = var.constraint_class
    }
    network {
      port "alertmanager" {
        static = 9093
        to     = 9093
      }
    }

    task "alertmanager" {
      driver = "exec"
      config {
        command = "local/alertmanager-${var.version}.linux-amd64/alertmanager"
        args    = [
          "--config.file=secrets/alertmanager.yml"
        ]
      }

      artifact {
        source = "https://github.com/prometheus/alertmanager/releases/download/v${var.version}/alertmanager-${var.version}.linux-amd64.tar.gz"
      }

      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/alertmanager.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
# The directory from which notification templates are read.
templates:
- '/etc/alertmanager/template/*.tmpl'
route:
  receiver: 'default-receiver'
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 3h
  routes:
  - match_re:
      service: .*
    receiver: default-receiver
    routes:
    - match:
        severity: critical
      receiver: 'default-receiver'
inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'instance']
receivers:
- name: 'default-receiver'
  webex_configs:
  - room_id: '98a26250-d1d9-11ec-bf18-111b73fff27f'
    message: >-
     {{ range .Alerts -}}
     *Alert:* {{ .Annotations.summary }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}

     *Description:* {{ .Annotations.description }}

     *Details:*
       {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
       {{ end }}
     {{ end }}
    http_config:
      authorization:
        type: Bearer
        credentials: ""
EOH
      }
      service {
        name       = "alertmanager"
        port       = "alertmanager"
        tags       = [ "alertmanager$${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "Alertmanager Check Live"
          type     = "http"
          path     = "/-/healthy"
          interval = "10s"
          timeout  = "2s"
        }
      }
      resources {
        cpu    = var.cpu
        memory = var.memory
      }
    }
  }
}
