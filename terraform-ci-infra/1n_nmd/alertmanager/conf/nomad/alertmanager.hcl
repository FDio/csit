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
    count             = ${group_count}

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
      driver          = "exec"

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
        command       = "local/alertmanager-${version}.linux-amd64/alertmanager"
        args          = [
          "--config.file=secrets/alertmanager.yml"
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
        destination     = "secrets/alertmanager.yml"
        left_delimiter  = "{{{"
        right_delimiter = "}}}"
        data            = <<EOH
# The directory from which notification templates are read.
templates:
- '/etc/alertmanager/template/*.tmpl'

#tls_config:
#  # CA certificate to validate the server certificate with.
#  ca_file: <filepath> ]
#
#  # Certificate and key files for client cert authentication to the server.
#  cert_file: <filepath>
#  key_file: <filepath>
#
#  # ServerName extension to indicate the name of the server.
#  # http://tools.ietf.org/html/rfc4366#section-3.1
#  server_name: <string>
#
#  # Disable validation of the server certificate.
#  insecure_skip_verify: true

# The root route on which each incoming alert enters.
route:
  receiver: '${slack_default_receiver}'

  # The labels by which incoming alerts are grouped together. For example,
  # multiple alerts coming in for cluster=A and alertname=LatencyHigh would
  # be batched into a single group.
  #
  # To aggregate by all possible labels use '...' as the sole label name.
  # This effectively disables aggregation entirely, passing through all
  # alerts as-is. This is unlikely to be what you want, unless you have
  # a very low alert volume or your upstream notification system performs
  # its own grouping. Example: group_by: [...]
  group_by: ['alertname']

  # When a new group of alerts is created by an incoming alert, wait at
  # least 'group_wait' to send the initial notification.
  # This way ensures that you get multiple alerts for the same group that start
  # firing shortly after another are batched together on the first
  # notification.
  group_wait: 30s

  # When the first notification was sent, wait 'group_interval' to send a batch
  # of new alerts that started firing for that group.
  group_interval: 5m

  # If an alert has successfully been sent, wait 'repeat_interval' to
  # resend them.
  repeat_interval: 3h

  # All the above attributes are inherited by all child routes and can
  # overwritten on each.
  # The child route trees.
  routes:
  - match_re:
      alertname: JenkinsJob.*
    receiver: ${slack_jenkins_receiver}
    routes:
    - match:
        severity: critical
      receiver: '${slack_jenkins_receiver}'

  - match_re:
      service: .*
    receiver: ${slack_default_receiver}
    routes:
    - match:
        severity: critical
      receiver: '${slack_default_receiver}'

# Inhibition rules allow to mute a set of alerts given that another alert is
# firing.
# We use this to mute any warning-level notifications if the same alert is
# already critical.
inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'instance']

receivers:
- name: '${slack_jenkins_receiver}'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/${slack_jenkins_api_key}'
    channel: '#${slack_jenkins_channel}'
    send_resolved: true
    icon_url: https://avatars3.githubusercontent.com/u/3380462
    title: |-
     [{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }} for {{ .CommonLabels.job }}
     {{- if gt (len .CommonLabels) (len .GroupLabels) -}}
       {{" "}}(
       {{- with .CommonLabels.Remove .GroupLabels.Names }}
         {{- range $index, $label := .SortedPairs -}}
           {{ if $index }}, {{ end }}
           {{- $label.Name }}="{{ $label.Value -}}"
         {{- end }}
       {{- end -}}
       )
     {{- end }}
    text: >-
     {{ range .Alerts -}}
     *Alert:* {{ .Annotations.summary }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}

     *Description:* {{ .Annotations.description }}

     *Details:*
       {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
       {{ end }}
     {{ end }}

- name: '${slack_default_receiver}'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/${slack_default_api_key}'
    channel: '#${slack_default_channel}'
    send_resolved: true
    icon_url: https://avatars3.githubusercontent.com/u/3380462
    title: |-
     [{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }} for {{ .CommonLabels.job }}
     {{- if gt (len .CommonLabels) (len .GroupLabels) -}}
       {{" "}}(
       {{- with .CommonLabels.Remove .GroupLabels.Names }}
         {{- range $index, $label := .SortedPairs -}}
           {{ if $index }}, {{ end }}
           {{- $label.Name }}="{{ $label.Value -}}"
         {{- end }}
       {{- end -}}
       )
     {{- end }}
    text: >-
     {{ range .Alerts -}}
     *Alert:* {{ .Annotations.summary }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}

     *Description:* {{ .Annotations.description }}

     *Details:*
       {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
       {{ end }}
     {{ end }}
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
          name          = "Alertmanager Check Live"
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