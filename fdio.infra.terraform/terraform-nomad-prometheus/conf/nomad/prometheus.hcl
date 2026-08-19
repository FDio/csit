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
  default = 2000
}

variable "version" {
  # Set the `NOMAD_VAR_version` environment variable to override the
  # default for the task.
  type    = string
  default = "3.14.0"
}

variable "memory" {
  # Set the `NOMAD_VAR_memory` environment variable to override the
  # default for the task.
  type    = number
  default = 4096
}

job "prometheus" {
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

  group "prometheus" {
    count = 4
    volume "prometheus-volume-1" {
      type      = "host"
      read_only = false
      source    = "prod-volume-data1-1"
    }
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
      port "prometheus" {
        static = 9090
        to     = 9090
      }
    }

    task "prometheus" {
      driver = "exec"
      volume_mount {
        volume      = "prometheus-volume-1"
        destination = "/data/"
        read_only   = false
      }
      config {
        command = "local/prometheus-${var.version}.linux-amd64/prometheus"
        args    = [
          "--config.file=secrets/prometheus.yml",
          "--web.config.file=secrets/web-config.yml",
          "--storage.tsdb.path=/data/prometheus/",
          "--storage.tsdb.retention.time=7d"
        ]
      }

      artifact {
        source = "https://github.com/prometheus/prometheus/releases/download/v${var.version}/prometheus-${var.version}.linux-amd64.tar.gz"
      }

      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/cert_file.crt"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
-----BEGIN CERTIFICATE-----
MIIFszCCA5ugAwIBAgIUDtmFbbnYaXbXH5ddtHi9l25wM7owDQYJKoZIhvcNAQEL
BQAwaTELMAkGA1UEBhMCU0sxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDEiMCAGA1UEAwwZcHJvbWV0aGV1cy5z
ZXJ2aWNlLmNvbnN1bDAeFw0yMjEyMzEyMDMxMDFaFw0yMzAxMzAyMDMxMDFaMGkx
CzAJBgNVBAYTAlNLMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRl
cm5ldCBXaWRnaXRzIFB0eSBMdGQxIjAgBgNVBAMMGXByb21ldGhldXMuc2Vydmlj
ZS5jb25zdWwwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCGH4Tyj+9G
wYJNb3ubIdr5r0/DZL6XEnRIMiz88TN2QmdwAGKyQqQd7ka0IkdDHPhpRuK8IV1g
ELQhKab7YJCa6zWuy+rQ6JFlotGC+2tIXd3MDriUd1VPVoX6fw/5zUK/2j6exBk4
iqxPXHchQLzZ0viUXhQIBS1IUMTbfc0vjA8U0uPgpmAR7ieePWFwmUDxjOLMvJw6
+goeOfaHhW4yYgT+kg7L3rT62G+KG6Op/p7k7BNZ6G6Y6K6uJ7Z/AayAClF2sPZz
UIGr0uEDvD4IcAsfQgpR5vK/SVBFU5+DSO68mm11m+8IH/HA6GvNSEvCRC0Wtrsm
Dyq+9S3wZ7tNi7msjQWWKTB1GvTbCbPE1G/q5GJdoKUnioys6AMP4DTEV9o3lCSg
0sjYnkSTKgRplnuY/7Y2qSNnD1Rw0ZneSkF+8ocgiYcTvtyOY2fkhlT2VaQLX987
m7892ikPvoCnc/LVeREWW7hCuIQ1E1CCqg304Kd9gCgKoOGXoYmC/3wgJW0RkaM0
x5DpNLYx0y11CPVg315dvprOuedap6J3CNhBE3fO8ymwepFTzTcWLWgSVWrRLZnx
Lgb4SPhjxPg6cCZptkmXrPA+9SgW8iNHd/Fer6MAs82Kcp2T1C+qq9RurL/jjxTD
JaFrwZC2lgWELToMyVDrkBJJbA/2cU9CMQIDAQABo1MwUTAdBgNVHQ4EFgQUx1Mi
fylZExNnIz0EkrPRdXYmHmAwHwYDVR0jBBgwFoAUx1MifylZExNnIz0EkrPRdXYm
HmAwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEAbvlpMg4YRTNe
0cgqMZky/GpNjvE/zFManUGgYns8TKyZ8U0laBxRQ4XU/fASwAcOBJYtrkG7w8z+
FaOUptaOlNGW1VWsPDJt8ZQ2gAcTwKSW2EsBWCmOUJVNH5F0f6fTSqIUIXyxhP2w
JVniSkfarhb/Y1EDCACdr7Xpu6iF+nQo2o4/HE4Wkto4qwvlrdApYv4dl5J1TWjq
72fO9axDlNnEGVxa3C3xvKOQqWrEUy/HqC9p4it1yCiq6IYVLyve0meVFBY9xNXU
137AN7ks4ouuR1FZQkhLtqFuIekSZ5l4G4alwdv1NB8vohJMuMJyk9DarTLqXcYU
1uypZSmgREn8ByYrj4ochkSpiPw7wgK4H1Aa2cy4KUuzmLLShYu6Mov7hyJDoJSe
JsDVNoEBuhql4jENATqbWT3pIgYwBvBEXuYXqekcNmVZkKiSOlsxKFfSz21HYDgA
lCu4SMtlRYHcm4TuoTuy/FEPxHSjFY3pMciJrnO/qUrv9LlWPe1wjKhZLRPEebTk
r+Oh+aVWpy3ps7shPTjczOrmQykWWBGAjndZjZi4VvZNRxkGZuNwzzZcEkzt0Db7
l83pTRD58mvLHWl2QXoBS3t7IM6sOMwQvPx1Inp7hb7UIpNsJQaUrhhfKqy0sK18
mXs4VRtrxYycXxsLbk0SaZGh+juT53M=
-----END CERTIFICATE-----
EOH
      }
      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/key_file.key"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
-----BEGIN PRIVATE KEY-----
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
775JbZNCKpaELqxy4BNPfRDEJGBh
-----END PRIVATE KEY-----
EOH
      }
      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/alerts.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
---
groups:
- name: "Consul"
  rules:
  - alert: ConsulServiceHealthcheckFailed
    expr: consul_catalog_service_node_healthy == 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Consul service healthcheck failed (instance {{ $labels.instance }})."
      description: "Service: `{{ $labels.service_name }}` Healthcheck: `{{ $labels.service_id }}`."
  - alert: ConsulMissingMasterNode
    expr: consul_raft_peers < 3
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Consul missing master node (instance {{ $labels.instance }})."
      description: "Numbers of consul raft peers should be 3, in order to preserve quorum."
  - alert: ConsulAgentUnhealthy
    expr: consul_health_node_status{status="critical"} == 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Consul agent unhealthy (instance {{ $labels.instance }})."
      description: "A Consul agent is down."
EOH
      }

      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/prometheus.yml"
        data            = <<EOH
---
global:
  scrape_interval:     5s
  scrape_timeout:      5s
  evaluation_interval: 5s

alerting:
  alertmanagers:
  - consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'alertmanager' ]

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'Nomad Cluster'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'nomad-client', 'nomad' ]
    relabel_configs:
    - source_labels: [__meta_consul_tags]
      regex: '(.*)http(.*)'
      action: keep
    metrics_path: /v1/metrics
    params:
      format: [ 'prometheus' ]

  - job_name: 'Consul Cluster'
    static_configs:
      - targets: [ '10.30.51.21:8500' ]
      - targets: [ '10.30.51.22:8500' ]
      - targets: [ '10.30.51.23:8500' ]
      - targets: [ '10.30.51.24:8500' ]
      - targets: [ '10.30.51.25:8500' ]
      - targets: [ '10.30.51.26:8500' ]
      - targets: [ '10.30.51.27:8500' ]
      - targets: [ '10.30.51.28:8500' ]
      - targets: [ '10.30.51.30:8500' ]
      - targets: [ '10.30.51.31:8500' ]
      - targets: [ '10.30.51.50:8500' ]
      - targets: [ '10.30.51.51:8500' ]
      - targets: [ '10.30.51.70:8500' ]
      - targets: [ '10.30.51.71:8500' ]
      - targets: [ '10.30.51.91:8500' ]
      - targets: [ '10.30.51.92:8500' ]
    metrics_path: /v1/agent/metrics
    params:
      format: [ 'prometheus' ]

  - job_name: 'Alertmanager'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'alertmanager' ]

  - job_name: 'Prometheus'
    honor_timestamps: true
    params:
      format:
      - prometheus
    scheme: https
    follow_redirects: true
    enable_http2: true
    consul_sd_configs:
    - server: {{ env "CONSUL_HTTP_ADDR" }}
      services:
      - prometheus
    tls_config:
      cert_file: cert_file.crt
      key_file: key_file.key
      insecure_skip_verify: true
EOH
      }

      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/web-config.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
---
tls_server_config:
  cert_file: cert_file.crt
  key_file: key_file.key
EOH
      }
      service {
        name       = "prometheus"
        port       = "prometheus"
        tags       = [ "prometheus$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Prometheus Check Live"
          type            = "http"
          path            = "/-/healthy"
          protocol        = "https"
          tls_skip_verify = true
          interval        = "10s"
          timeout         = "2s"
        }
      }
      resources {
        cpu    = var.cpu
        memory = var.memory
      }
    }
  }
}
