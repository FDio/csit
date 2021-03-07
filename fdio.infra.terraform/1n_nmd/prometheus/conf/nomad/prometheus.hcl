job "${job_name}" {
  # The "region" parameter specifies the region in which to execute the job.
  # If omitted, this inherits the default region name of "global".
  # region = "global"
  #
  # The "datacenters" parameter specifies the list of datacenters which should
  # be considered when placing this task. This must be provided.
  datacenters         = "${datacenters}"

  # The "type" parameter controls the type of job, which impacts the scheduler's
  # decision on placement. This configuration is optional and defaults to
  # "service". For a full list of job types and their differences, please see
  # the online documentation.
  #
  # For more information, please see the online documentation at:
  #
  #     https://www.nomadproject.io/docs/jobspec/schedulers
  #
  type                = "service"

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

  # The reschedule stanza specifies the group's rescheduling strategy. If
  # specified at the job level, the configuration will apply to all groups
  # within the job. If the reschedule stanza is present on both the job and the
  # group, they are merged with the group stanza taking the highest precedence
  # and then the job.
  reschedule {
    delay             = "30s"
    delay_function    = "constant"
    unlimited         = true
  }

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group
  #
  group "prod-group1-${service_name}" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count               = ${group_count}

    # The restart stanza configures a tasks's behavior on task failure. Restarts
    # happen on the client that is running the task.
    #
    # https://www.nomadproject.io/docs/job-specification/restart
    #
    restart {
      interval  = "30m"
      attempts  = 40
      delay     = "15s"
      mode      = "delay"
    }

    # The volume stanza allows the group to specify that it requires a given
    # volume from the cluster.
    #
    # For more information and examples on the "volume" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/volume
    #
    %{ if use_host_volume }
    volume "prod-volume1-${service_name}" {
      type              = "host"
      read_only         = false
      source            = "${host_volume}"
    }
    %{ endif }

    # The constraint allows restricting the set of eligible nodes. Constraints
    # may filter on attributes or client metadata.
    #
    # For more information and examples on the "volume" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/constraint
    #
    constraint {
      attribute         = "$${attr.cpu.arch}"
      operator          = "!="
      value             = "arm64"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task
    #
    task "prod-task1-${service_name}" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver            = "exec"

      %{ if use_host_volume }
      volume_mount {
        volume          = "prod-volume1-${service_name}"
        destination     = "${data_dir}"
        read_only       = false
      }
      %{ endif }

      %{ if use_vault_provider }
      vault {
        policies        = "${vault_kv_policy_name}"
      }
      %{ endif }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command         = "local/prometheus-${version}.linux-amd64/prometheus"
        args            = [
          "--config.file=secrets/prometheus.yml",
          "--storage.tsdb.path=${data_dir}prometheus/",
          "--storage.tsdb.retention.time=15d"
        ]
      }

      # The artifact stanza instructs Nomad to fetch and unpack a remote resource,
      # such as a file, tarball, or binary. Nomad downloads artifacts using the
      # popular go-getter library, which permits downloading artifacts from a
      # variety of locations using a URL as the input source.
      #
      # For more information and examples on the "artifact" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/artifact
      #
      artifact {
        source          = "${url}"
      }

      # The "template" stanza instructs Nomad to manage a template, such as
      # a configuration file or script. This template can optionally pull data
      # from Consul or Vault to populate runtime configuration data.
      #
      # For more information and examples on the "template" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/template
      #
      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/alerts.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
---
groups:
- name: "Jenkins Job Health Exporter"
  rules:
  - alert: JenkinsJobHealthExporterFailures
    expr: jenkins_job_failure{id=~".*"} > jenkins_job_success{id=~".*"}
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Jenkins Job Health detected high failure rate on jenkins jobs."
      description: "Job: {{ $labels.id }}"
  - alert: JenkinsJobHealthExporterUnstable
    expr: jenkins_job_unstable{id=~".*"} > jenkins_job_success{id=~".*"}
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Jenkins Job Health detected high unstable rate on jenkins jobs."
      description: "Job: {{ $labels.id }}"
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
- name: "Hosts"
  rules:
  - alert: NodeDown
    expr: up == 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus target missing (instance {{ $labels.instance }})."
      description: "A Prometheus target has disappeared. An exporter might be crashed."
  - alert: HostHighCpuLoad
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 95
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host high CPU load (instance {{ $labels.instance }})."
      description: "CPU load is > 95%."
  - alert: HostOutOfMemory
    expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host out of memory (instance {{ $labels.instance }})."
      description: "Node memory is filling up (< 10% left)."
  - alert: HostOomKillDetected
    expr: increase(node_vmstat_oom_kill[1m]) > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host OOM kill detected (instance {{ $labels.instance }})."
      description: "OOM kill detected."
  - alert: HostMemoryUnderMemoryPressure
    expr: rate(node_vmstat_pgmajfault[1m]) > 1000
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host memory under memory pressure (instance {{ $labels.instance }})."
      description: "The node is under heavy memory pressure. High rate of major page faults."
  - alert: HostOutOfDiskSpace
    expr: (node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes < 10 and ON (instance, device, mountpoint) node_filesystem_readonly == 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host out of disk space (instance {{ $labels.instance }})."
      description: "Disk is almost full (< 10% left)."
  - alert: HostRaidDiskFailure
    expr: node_md_disks{state="failed"} > 0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Host RAID disk failure (instance {{ $labels.instance }})."
      description: "At least one device in RAID array on {{ $labels.instance }} failed. Array {{ $labels.md_device }} needs attention and possibly a disk swap."
  - alert: HostConntrackLimit
    expr: node_nf_conntrack_entries / node_nf_conntrack_entries_limit > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Host conntrack limit (instance {{ $labels.instance }})."
      description: "The number of conntrack is approching limit."
  - alert: HostNetworkInterfaceSaturated
    expr: (rate(node_network_receive_bytes_total{device!~"^tap.*"}[1m]) + rate(node_network_transmit_bytes_total{device!~"^tap.*"}[1m])) / node_network_speed_bytes{device!~"^tap.*"} > 0.8
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Host Network Interface Saturated (instance {{ $labels.instance }})."
      description: "The network interface {{ $labels.interface }} on {{ $labels.instance }} is getting overloaded."
  - alert: HostSystemdServiceCrashed
    expr: node_systemd_unit_state{state="failed"} == 1
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host SystemD service crashed (instance {{ $labels.instance }})."
      description: "SystemD service crashed."
  - alert: HostEdacCorrectableErrorsDetected
    expr: increase(node_edac_correctable_errors_total[1m]) > 0
    for: 0m
    labels:
      severity: info
    annotations:
      summary: "Host EDAC Correctable Errors detected (instance {{ $labels.instance }})."
      description: '{{ $labels.instance }} has had {{ printf "%.0f" $value }} correctable memory errors reported by EDAC in the last 5 minutes.'
  - alert: HostEdacUncorrectableErrorsDetected
    expr: node_edac_uncorrectable_errors_total > 0
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Host EDAC Uncorrectable Errors detected (instance {{ $labels.instance }})."
      description: '{{ $labels.instance }} has had {{ printf "%.0f" $value }} uncorrectable memory errors reported by EDAC in the last 5 minutes.'
- name: "Min.io"
  rules:
  - alert: MinioDiskOffline
    expr: minio_offline_disks > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Minio disk offline (instance {{ $labels.instance }})"
      description: "Minio disk is offline."
  - alert: MinioStorageSpaceExhausted
    expr: minio_disk_storage_free_bytes / 1024 / 1024 / 1024 < 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Minio storage space exhausted (instance {{ $labels.instance }})."
      description: "Minio storage space is low (< 10 GB)."
- name: "Prometheus"
  rules:
  - alert: PrometheusConfigurationReloadFailure
    expr: prometheus_config_last_reload_successful != 1
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Prometheus configuration reload failure (instance {{ $labels.instance }})."
      description: "Prometheus configuration reload error."
  - alert: PrometheusTooManyRestarts
    expr: changes(process_start_time_seconds{job=~"prometheus|pushgateway|alertmanager"}[15m]) > 2
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Prometheus too many restarts (instance {{ $labels.instance }})."
      description: "Prometheus has restarted more than twice in the last 15 minutes. It might be crashlooping."
  - alert: PrometheusAlertmanagerConfigurationReloadFailure
    expr: alertmanager_config_last_reload_successful != 1
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Prometheus AlertManager configuration reload failure (instance {{ $labels.instance }})."
      description: "AlertManager configuration reload error."
  - alert: PrometheusRuleEvaluationFailures
    expr: increase(prometheus_rule_evaluation_failures_total[3m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus rule evaluation failures (instance {{ $labels.instance }})."
      description: "Prometheus encountered {{ $value }} rule evaluation failures, leading to potentially ignored alerts."
  - alert: PrometheusTargetScrapingSlow
    expr: prometheus_target_interval_length_seconds{quantile="0.9"} > 60
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Prometheus target scraping slow (instance {{ $labels.instance }})."
      description: "Prometheus is scraping exporters slowly."
  - alert: PrometheusTsdbCompactionsFailed
    expr: increase(prometheus_tsdb_compactions_failed_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus TSDB compactions failed (instance {{ $labels.instance }})."
      description: "Prometheus encountered {{ $value }} TSDB compactions failures."
  - alert: PrometheusTsdbHeadTruncationsFailed
    expr: increase(prometheus_tsdb_head_truncations_failed_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus TSDB head truncations failed (instance {{ $labels.instance }})."
      description: "Prometheus encountered {{ $value }} TSDB head truncation failures."
  - alert: PrometheusTsdbWalCorruptions
    expr: increase(prometheus_tsdb_wal_corruptions_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus TSDB WAL corruptions (instance {{ $labels.instance }})."
      description: "Prometheus encountered {{ $value }} TSDB WAL corruptions."
  - alert: PrometheusTsdbWalTruncationsFailed
    expr: increase(prometheus_tsdb_wal_truncations_failed_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus TSDB WAL truncations failed (instance {{ $labels.instance }})."
      description: "Prometheus encountered {{ $value }} TSDB WAL truncation failures."
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
      - targets: [ '10.30.51.28:8500' ]
      - targets: [ '10.30.51.29:8500' ]
      - targets: [ '10.30.51.30:8500' ]
      - targets: [ '10.30.51.32:8500' ]
      - targets: [ '10.30.51.33:8500' ]
      - targets: [ '10.30.51.34:8500' ]
      - targets: [ '10.30.51.35:8500' ]
      - targets: [ '10.30.51.39:8500' ]
      - targets: [ '10.30.51.40:8500' ]
      - targets: [ '10.30.51.50:8500' ]
      - targets: [ '10.30.51.51:8500' ]
      - targets: [ '10.30.51.65:8500' ]
      - targets: [ '10.30.51.66:8500' ]
      - targets: [ '10.30.51.67:8500' ]
      - targets: [ '10.30.51.68:8500' ]
      - targets: [ '10.30.51.70:8500' ]
      - targets: [ '10.30.51.71:8500' ]
      - targets: [ '10.32.8.14:8500' ]
      - targets: [ '10.32.8.15:8500' ]
      - targets: [ '10.32.8.16:8500' ]
      - targets: [ '10.32.8.17:8500' ]
    metrics_path: /v1/agent/metrics
    params:
      format: [ 'prometheus' ]

  - job_name: 'Blackbox Exporter (icmp)'
    static_configs:
      - targets: [ 'gerrit.fd.io' ]
      - targets: [ 'jenkins.fd.io' ]
      - targets: [ '10.30.51.32' ]
    params:
      module: [ 'icmp_v4' ]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
    metrics_path: /probe

  - job_name: 'Blackbox Exporter (http)'
    static_configs:
      - targets: [ 'gerrit.fd.io' ]
      - targets: [ 'jenkins.fd.io' ]
    params:
      module: [ 'http_2xx' ]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
    metrics_path: /probe

  - job_name: 'cAdvisor Exporter'
    static_configs:
      - targets: [ '10.30.51.28:8080' ]
      - targets: [ '10.30.51.29:8080' ]
      - targets: [ '10.30.51.30:8080' ]
      #- targets: [ '10.30.51.32:8080' ]
      - targets: [ '10.30.51.33:8080' ]
      - targets: [ '10.30.51.34:8080' ]
      - targets: [ '10.30.51.35:8080' ]
      - targets: [ '10.30.51.39:8080' ]
      - targets: [ '10.30.51.40:8080' ]
      - targets: [ '10.30.51.50:8080' ]
      - targets: [ '10.30.51.51:8080' ]
      - targets: [ '10.30.51.65:8080' ]
      - targets: [ '10.30.51.66:8080' ]
      - targets: [ '10.30.51.67:8080' ]
      - targets: [ '10.30.51.68:8080' ]
      - targets: [ '10.30.51.70:8080' ]
      - targets: [ '10.30.51.71:8080' ]
      - targets: [ '10.32.8.14:8080' ]
      - targets: [ '10.32.8.15:8080' ]
      - targets: [ '10.32.8.16:8080' ]
      - targets: [ '10.32.8.17:8080' ]

  - job_name: 'Jenkins Job Health Exporter'
    static_configs:
      - targets: [ '10.30.51.32:9186' ]
    metric_relabel_configs:
      - source_labels: [ __name__ ]
        regex: '^(vpp.*|csit.*)_(success|failure|total|unstable|reqtime_ms)$'
        action: replace
        replacement: '$1'
        target_label: id
      - source_labels: [ __name__ ]
        regex: '^(vpp.*|csit.*)_(success|failure|total|unstable|reqtime_ms)$'
        replacement: 'jenkins_job_$2'
        target_label: __name__

  - job_name: 'Node Exporter'
    static_configs:
      - targets: [ '10.30.51.28:9100' ]
      - targets: [ '10.30.51.29:9100' ]
      - targets: [ '10.30.51.30:9100' ]
      - targets: [ '10.30.51.32:9100' ]
      - targets: [ '10.30.51.33:9100' ]
      - targets: [ '10.30.51.34:9100' ]
      - targets: [ '10.30.51.35:9100' ]
      - targets: [ '10.30.51.39:9100' ]
      - targets: [ '10.30.51.40:9100' ]
      - targets: [ '10.30.51.50:9100' ]
      - targets: [ '10.30.51.51:9100' ]
      - targets: [ '10.30.51.65:9100' ]
      - targets: [ '10.30.51.66:9100' ]
      - targets: [ '10.30.51.67:9100' ]
      - targets: [ '10.30.51.68:9100' ]
      - targets: [ '10.30.51.70:9100' ]
      - targets: [ '10.30.51.71:9100' ]
      - targets: [ '10.32.8.14:9100' ]
      - targets: [ '10.32.8.15:9100' ]
      - targets: [ '10.32.8.16:9100' ]
      - targets: [ '10.32.8.17:9100' ]

  - job_name: 'Alertmanager'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'alertmanager' ]

  - job_name: 'Grafana'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'grafana' ]

  - job_name: 'Prometheus'
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'prometheus' ]

  - job_name: 'Minio'
    bearer_token: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQ3NjQ1ODEzMzcsImlzcyI6InByb21ldGhldXMiLCJzdWIiOiJtaW5pbyJ9.oeTw3EIaiFmlDikrHXWiWXMH2vxLfDLkfjEC7G2N3M_keH_xyA_l2ofLLNYtopa_3GCEZnxLQdPuFZrmgpkDWg
    consul_sd_configs:
    - server: '{{ env "NOMAD_IP_prometheus" }}:8500'
      services: [ 'storage' ]
    metrics_path: /minio/prometheus/metrics
EOH
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name            = "${service_name}"
        port            = "${service_name}"
        tags            = [ "${service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name          = "Prometheus Check Live"
          type          = "http"
          path          = "/-/healthy"
          interval      = "10s"
          timeout       = "2s"
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
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu             = ${cpu}
        memory          = ${mem}
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
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${service_name}" {
            static      = ${port}
          }
        }
      }
    }
  }
}