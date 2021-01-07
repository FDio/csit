job "${job_name}" {
  # The "region" parameter specifies the region in which to execute the job.
  # If omitted, this inherits the default region name of "global".
  # region = "global"
  #
  # The "datacenters" parameter specifies the list of datacenters which should
  # be considered when placing this task. This must be provided.
  datacenters = "${datacenters}"

  # The "type" parameter controls the type of job, which impacts the scheduler's
  # decision on placement. This configuration is optional and defaults to
  # "service". For a full list of job types and their differences, please see
  # the online documentation.
  #
  # For more information, please see the online documentation at:
  #
  #     https://www.nomadproject.io/docs/jobspec/schedulers.html
  #
  type        = "service"

  update {
    # The "max_parallel" parameter specifies the maximum number of updates to
    # perform in parallel. In this case, this specifies to update a single task
    # at a time.
    max_parallel      = 1

    health_check      = "checks"

    # The "min_healthy_time" parameter specifies the minimum time the allocation
    # must be in the healthy state before it is marked as healthy and unblocks
    # further allocations from being updated.
    min_healthy_time  = "10s"

    # The "healthy_deadline" parameter specifies the deadline in which the
    # allocation must be marked as healthy after which the allocation is
    # automatically transitioned to unhealthy. Transitioning to unhealthy will
    # fail the deployment and potentially roll back the job if "auto_revert" is
    # set to true.
    healthy_deadline  = "3m"

    # The "progress_deadline" parameter specifies the deadline in which an
    # allocation must be marked as healthy. The deadline begins when the first
    # allocation for the deployment is created and is reset whenever an allocation
    # as part of the deployment transitions to a healthy state. If no allocation
    # transitions to the healthy state before the progress deadline, the
    # deployment is marked as failed.
    progress_deadline = "10m"

%{ if use_canary }
    # The "canary" parameter specifies that changes to the job that would result
    # in destructive updates should create the specified number of canaries
    # without stopping any previous allocations. Once the operator determines the
    # canaries are healthy, they can be promoted which unblocks a rolling update
    # of the remaining allocations at a rate of "max_parallel".
    #
    # Further, setting "canary" equal to the count of the task group allows
    # blue/green deployments. When the job is updated, a full set of the new
    # version is deployed and upon promotion the old version is stopped.
    canary            = 1

    # Specifies if the job should auto-promote to the canary version when all
    # canaries become healthy during a deployment. Defaults to false which means
    # canaries must be manually updated with the nomad deployment promote
    # command.
    auto_promote      = true

    # The "auto_revert" parameter specifies if the job should auto-revert to the
    # last stable job on deployment failure. A job is marked as stable if all the
    # allocations as part of its deployment were marked healthy.
    auto_revert       = true
%{ endif }
  }

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-alertmanager" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count             = ${alertmanager_group_count}

    constraint {
      attribute       = "$${node.unique.name}"
      value           = "s41-nomad-x86_64"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-alertmanager" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "prom/alertmanager:${alertmanager_version}"
        dns_servers   = [ "$${attr.unique.network.ip-address}" ]
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name          = "${alertmanager_service_name}"
        port          = "alertmanager"
        tags          = [ "${alertmanager_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name        = "Alertmanager Check Live"
          type        = "http"
          path        = "/-/healthy"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      # For more information and examples on the "resources" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/resources.html
      #
      resources {
        cpu        = ${alertmanager_cpu}
        memory     = ${alertmanager_mem}
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        # For more information and examples on the "template" stanza, please see
        # the online documentation at:
        #
        #     https://www.nomadproject.io/docs/job-specification/network.html
        #
        network {
          port "alertmanager" {
            static = ${alertmanager_port}
          }
        }
      }
    }
  }

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-prometheus" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count             = ${prometheus_group_count}

    constraint {
      attribute       = "$${node.unique.name}"
      value           = "s41-nomad-x86_64"
    }

    ephemeral_disk {
      size            = "50000"
      sticky          = true
      migrate         = true
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-prometheus" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "prom/prometheus:${prometheus_version}"
        dns_servers   = [ "$${attr.unique.network.ip-address}" ]
        volumes       = [
          "local/alerts.yml:/etc/prometheus/alerts.yml",
          "local/nodes.json:/etc/prometheus/nodes.json",
          "local/prometheus.yml:/etc/prometheus/prometheus.yml"
        ]
      }

      # The "template" stanza instructs Nomad to manage a template, such as
      # a configuration file or script. This template can optionally pull data
      # from Consul or Vault to populate runtime configuration data.
      #
      # For more information and examples on the "template" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/template.html
      #
      template {
        change_mode     = "noop"
        destination     = "local/alerts.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
---
groups:
- name: "Consul"
  rules:
  - alert: ConsulServiceHealthcheckFailed
    expr: consul_catalog_service_node_healthy == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Consul service healthcheck failed (instance {{ $labels.instance }})"
      description: "Service: `{{ $labels.service_name }}` Healthcheck: `{{ $labels.service_id }}`\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: ConsulMissingMasterNode
    expr: consul_raft_peers < 3
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Consul missing master node (instance {{ $labels.instance }})"
      description: "Numbers of consul raft peers should be 3, in order to preserve quorum.\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: ConsulAgentUnhealthy
    expr: consul_health_node_status{status="critical"} == 1
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Consul agent unhealthy (instance {{ $labels.instance }})"
      description: "A Consul agent is down\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
- name: "Hosts"
  rules:
  - alert: NodeDown
    expr: up == 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus target missing (instance {{ $labels.instance }})"
      description: "A Prometheus target has disappeared. An exporter might be crashed.\n VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostHighCpuLoad
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100) > 80
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host high CPU load (instance {{ $labels.instance }})"
      description: "CPU load is > 80%\n VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostOutOfMemory
    expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host out of memory (instance {{ $labels.instance }})"
      description: "Node memory is filling up (< 10% left)\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostOomKillDetected
    expr: increase(node_vmstat_oom_kill[1m]) > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host OOM kill detected (instance {{ $labels.instance }})"
      description: "OOM kill detected\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostMemoryUnderMemoryPressure
    expr: rate(node_vmstat_pgmajfault[1m]) > 1000
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host memory under memory pressure (instance {{ $labels.instance }})"
      description: "The node is under heavy memory pressure. High rate of major page faults\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostOutOfDiskSpace
    expr: (node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes < 10 and ON (instance, device, mountpoint) node_filesystem_readonly == 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host out of disk space (instance {{ $labels.instance }})"
      description: "Disk is almost full (< 10% left)\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostRaidDiskFailure
    expr: node_md_disks{state="failed"} > 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host RAID disk failure (instance {{ $labels.instance }})"
      description: "At least one device in RAID array on {{ $labels.instance }} failed. Array {{ $labels.md_device }} needs attention and possibly a disk swap\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: HostConntrackLimit
    expr: node_nf_conntrack_entries / node_nf_conntrack_entries_limit > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Host conntrack limit (instance {{ $labels.instance }})"
      description: "The number of conntrack is approching limit\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
- name: "Min.io"
  rules:
  - alert: MinioDiskOffline
    expr: minio_offline_disks > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Minio disk offline (instance {{ $labels.instance }})"
      description: "Minio disk is offline\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
  - alert: MinioStorageSpaceExhausted
    expr: minio_disk_storage_free_bytes / 1024 / 1024 / 1024 < 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Minio storage space exhausted (instance {{ $labels.instance }})"
      description: "Minio storage space is low (< 10 GB)\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"
EOH
      }

      template {
        change_mode   = "noop"
        destination   = "local/nodes.json"
        data          = <<EOH
[
  {
    "targets": [
      "10.30.51.28:9100",
      "10.30.51.28:9107",
      "10.30.51.28:8080"
    ],
    "labels": {
      "job": "s41-nomad"
    }
  },
  {
    "targets": [
      "10.30.51.50:9100",
      "10.30.51.50:9107",
      "10.30.51.50:8080"
    ],
    "labels": {
      "job": "s1-t11-sut1"
    }
  },
  {
    "targets": [
      "10.30.51.51:9100",
      "10.30.51.51:9107",
      "10.30.51.51:8080"
    ],
    "labels": {
      "job": "s2-t12-sut1"
    }
  }
]
EOH
      }

      template {
        change_mode   = "noop"
        destination   = "local/prometheus.yml"
        data          = <<EOH
---
global:
  scrape_interval:     5s
  evaluation_interval: 5s

alerting:
  alertmanagers:
  - consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'alertmanager' ]

rule_files:
  - "alerts.yml"

scrape_configs:

  - job_name: 'Nomad Cluster'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
    relabel_configs:
    - source_labels: [ '__meta_consul_tags' ]
      regex: '(.*)http(.*)'
      action: keep
    scrape_interval: 5s
    metrics_path: /v1/metrics
    params:
      format: [ 'prometheus' ]

  - job_name: 'Min.io Storage'
    bearer_token: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ3NjQ1ODEzMzcsImlzcyI6InByb21ldGhldXMiLCJzdWIiOiJtaW5pbyJ9.oeTw3EIaiFmlDikrHXWiWXMH2vxLfDLkfjEC7G2N3M_keH_xyA_l2ofLLNYtopa_3GCEZnxLQdPuFZrmgpkDWg
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'storage' ]
    scrape_interval: 5s
    metrics_path: /minio/prometheus/metrics
    scheme: http
    params:
      format: [ 'prometheus' ]

  - job_name: 'Alertmanager'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'alertmanager' ]

  - job_name: 'Nodes'
    file_sd_configs:
    - files:
      - 'nodes.json'

#tls_server_config:
#  cert_file: <filename>
#  key_file: <filename>
#basic_auth_users:
#  [ <string>: <secret> ... ]
EOH
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name       = "${prometheus_service_name}"
        port       = "prometheus"
        tags       = [ "${prometheus_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "Prometheus Check Live"
          type     = "http"
          path     = "/-/healthy"
          interval = "10s"
          timeout  = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      # For more information and examples on the "resources" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/resources.html
      #
      resources {
        cpu        = ${prometheus_cpu}
        memory     = ${prometheus_mem}
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        # For more information and examples on the "template" stanza, please see
        # the online documentation at:
        #
        #     https://www.nomadproject.io/docs/job-specification/network.html
        #
        network {
          port "prometheus" {
            static = ${prometheus_port}
          }
        }
      }
    }
  }

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-grafana" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count             = 1

    constraint {
      attribute       = "$${node.unique.name}"
      value           = "s41-nomad-x86_64"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-grafana" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "grafana/grafana:latest"
        dns_servers   = [ "$${attr.unique.network.ip-address}" ]
        volumes       = [
          "secrets/prometheus.yml:/etc/grafana/provisioning/datasources/prometheus.yml",
          "secrets/dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml",
          "secrets/grafana.ini:/etc/grafana/grafana.ini",
          "secrets/893.json/download:/etc/grafana/provisioning/dashboards/893.json",
          "secrets/1860.json/download:/etc/grafana/provisioning/dashboards/1860.json",
          "secrets/13396.json/download:/etc/grafana/provisioning/dashboards/13396.json"
        ]
      }

      artifact {
        source        = "https://grafana.com/api/dashboards/893/revisions/5/download"
        destination   = "secrets/893.json"
      }

      artifact {
        source        = "https://grafana.com/api/dashboards/1860/revisions/21/download"
        destination   = "secrets/1860.json"
      }

      artifact {
        source        = "https://grafana.com/api/dashboards/13396/revisions/3/download"
        destination   = "secrets/13396.json"
      }

      template {
        change_mode   = "noop"
        destination   = "secrets/prometheus.yml"
        data          = <<EOH
apiVersion: 1
datasources:
- name: Prometheus
  type: prometheus
  access: direct
  orgId: 1
  url: http://prometheus.service.consul:9090
  basicAuth: false
  isDefault: true
  version: 1
  editable: false
EOH
      }

      template {
        change_mode   = "noop"
        destination   = "secrets/dashboards.yml"
        data          = <<EOH
apiVersion: 1
providers:
- name: 'Prometheus'
  orgId: 1
  folder: ''
  type: file
  disableDeletion: false
  editable: false
  options:
    path: /etc/grafana/provisioning/dashboards
EOH
      }

      template {
        change_mode   = "noop"
        destination   = "secrets/grafana.ini"
        data          = <<EOH
app_mode = production

[server]
protocol = http
http_port = 3000
root_url = http://grafana.service.consul:3000
enable_gzip = true
;cert_file =
;cert_key =

[security]
admin_user = grafanauser
admin_password = Grafana1234
secret_key = SW2YcwTIb9zpOOhoPsMm

[users]
allow_sign_up = false
allow_org_create = false
auto_assign_org = true
auto_assign_org_role = Viewer
default_theme = dark

[auth.basic]
enabled = true

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[log]
mode = console
level = info

[log.console]
level = info
format = console
EOH
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name              = "grafana"
        port              = "grafana"
        tags              = [ "grafana$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Grafana Check Live"
          type            = "http"
          protocol        = "http"
#          header {
#            Authorization = ["Basic Z3JhZmFuYXVzZXIsR3JhZmFuYTEyMzQ="]
#          }
          tls_skip_verify = true
          path            = "/api/health"
          interval        = "10s"
          timeout         = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      # For more information and examples on the "resources" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/resources.html
      #
      resources {
        cpu           = 1000
        memory        = 256
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        # For more information and examples on the "template" stanza, please see
        # the online documentation at:
        #
        #     https://www.nomadproject.io/docs/job-specification/network.html
        #
        network {
          port "grafana" {
            static    = 3000
          }
        }
      }
    }
  }
}