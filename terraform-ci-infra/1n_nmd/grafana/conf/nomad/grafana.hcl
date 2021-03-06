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
    count             = ${group_count}


    # The constraint allows restricting the set of eligible nodes. Constraints
    # may filter on attributes or client metadata.
    #
    # For more information and examples on the "volume" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/constraint
    #
    constraint {
      attribute       = "$${attr.cpu.arch}"
      operator        = "!="
      value           = "arm64"
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
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "${image}"
        volumes       = [
          "secrets/prometheus.yml:/etc/grafana/provisioning/datasources/prometheus.yml",
          "secrets/dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml",
          "secrets/grafana.ini:/etc/grafana/grafana.ini",
          "secrets/node_exporter.json:/etc/grafana/provisioning/dashboards/node_exporter.json",
          "secrets/docker_cadvisor.json:/etc/grafana/provisioning/dashboards/docker_cadvisor.json",
          "secrets/nomad.json:/etc/grafana/provisioning/dashboards/nomad.json",
          "secrets/consul.json:/etc/grafana/provisioning/dashboards/consul.json",
          "secrets/prometheus.json:/etc/grafana/provisioning/dashboards/prometheus.json",
          "secrets/blackbox_exporter_http.json:/etc/grafana/provisioning/dashboards/blackbox_exporter_http.json",
          "secrets/blackbox_exporter_icmp.json:/etc/grafana/provisioning/dashboards/blackbox_exporter_icmp.json"
        ]
      }

      artifact {
        # Prometheus Node Exporter
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/node_exporter.json"
        destination   = "secrets/"
      }

      artifact {
        # Docker cAdvisor
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/docker_cadvisor.json"
        destination   = "secrets/"
      }

      artifact {
        # Nomad
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/nomad.json"
        destination   = "secrets/"
      }

      artifact {
        # Consul
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/consul.json"
        destination   = "secrets/"
      }

      artifact {
        # Prometheus
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/prometheus.json"
        destination   = "secrets/"
      }

      artifact {
        # Prometheus Blackbox Exporter HTTP
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/blackbox_exporter_http.json"
        destination   = "secrets/"
      }

      artifact {
        # Prometheus Blackbox Exporter ICMP
        source        = "https://raw.githubusercontent.com/pmikus/grafana-dashboards/main/blackbox_exporter_icmp.json"
        destination   = "secrets/"
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
        change_mode   = "noop"
        change_signal = "SIGINT"
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
        change_signal = "SIGINT"
        destination   = "secrets/dashboards.yml"
        data          = <<EOH
apiVersion: 1
providers:
- name: dashboards
  type: file
  disableDeletion: false
  updateIntervalSeconds: 10
  allowUiUpdates: false
  options:
    path: /etc/grafana/provisioning/dashboards
    foldersFromFilesStructure: true
EOH
      }

      template {
        change_mode   = "noop"
        change_signal = "SIGINT"
        destination   = "secrets/grafana.ini"
        data          = <<EOH
app_mode = production

[metrics]
enabled = true

[server]
protocol = http
http_port = ${port}
root_url = http://${service_name}.service.consul:${port}
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
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name              = "${service_name}"
        port              = "${service_name}"
        tags              = [ "${service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Grafana Check Live"
          type            = "http"
          protocol        = "http"
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
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu               = ${cpu}
        memory            = ${mem}
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
            static        = ${port}
          }
        }
      }
    }
  }
}