job "${job_name}" {
  # The "region" parameter specifies the region in which to execute the job.
  # If omitted, this inherits the default region name of "global".
  # region = "global"
  #
  # The "datacenters" parameter specifies the list of datacenters which should
  # be considered when placing this task. This must be provided.
  datacenters = "${datacenters}"

  # The "type" parameter controls the type of job, which impacts the scheduler's
  # decision on placement. For a full list of job types and their differences,
  # please see the online documentation.
  #
  # For more information, please see the online documentation at:
  #
  #     https://www.nomadproject.io/docs/jobspec/schedulers.html
  #
  type        = "system"

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
  group "prod-group1-beats" {

    restart {
      interval        = "1m"
      attempts        = 3
      delay           = "15s"
      mode            = "delay"
    }

    task "prod-task1-filebeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "docker.elastic.co/beats/filebeat:${version}"
        dns_servers  = [ "$${attr.unique.network.ip-address}" ]
        privileged   = true
        volumes      = [
          "/var/lib/docker/containers:/var/lib/docker/containers",
          "/var/run/docker.sock:/var/run/docker.sock"
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
        data          = <<EOF
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/syslog
    - /var/log/*.log
- type: container
  enabled: false
  paths:
    -/var/lib/docker/containers/*/*.log
  stream: all
output.elasticsearch:
  enabled: true
  hosts: ["elastic-rest.service.consul:9200"]
  compression_level: 0
  escape_html: true
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  worker: 1
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
setup.kibana:
  host: "kibana.service.consul:5601"
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  #path: ""
  #space.id: ""
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "/usr/share/packetbeat/filebeat.yml"
      }
    }

    task "prod-task1-metricbeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "docker.elastic.co/beats/metricbeat:${version}"
        dns_servers  = [ "$${attr.unique.network.ip-address}" ]
        privileged   = true
#        command      = "metricbeat"
        args = [
          "-e", "-system.hostfs=/hostfs"
        ]
        volumes      = [
          "/var/run/docker.sock:/var/run/docker.sock:ro",
          "/sys/fs/cgroup:/hostfs/sys/fs/cgroup:ro",
          "/proc:/hostfs/proc:ro",
          "/:/hostfs:ro"
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
        data         = <<EOF
metricbeat.config.modules:
  path: $${path.config}/modules.d/*.yml
  reload.period: 10s
  reload.enabled: false
metricbeat.max_start_delay: 10s
metricbeat.modules:
- module: system
  metricsets:
    - cpu
    - load
    - memory
    - network
    - process
    - process_summary
    - uptime
    - socket_summary
    - core
    - diskio
    #- filesystem
    - fsstat
    #- raid
    #- socket
    - service
  enabled: true
  period: 10s
  processes: ['.*']
  cpu.metrics:  ["percentages","normalized_percentages"]
  core.metrics: ["percentages"]
- module: consul
  metricsets:
  - agent
  enabled: true
  period: 10s
  hosts: ["localhost:8500"]
- module: docker
  metricsets:
    - "container"
    - "cpu"
    - "diskio"
    - "event"
    - "healthcheck"
    - "info"
    - "image"
    - "memory"
    - "network"
  hosts: ["unix:///var/run/docker.sock"]
  period: 10s
  enabled: true
output.elasticsearch:
  enabled: true
  hosts: ["elastic-rest.service.consul:9200"]
  compression_level: 0
  escape_html: true
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  worker: 1
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
setup.kibana:
  host: "elastic-kibana.service.consul:5601"
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  #path: ""
  #space.id: ""
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "/usr/share/packetbeat//metricbeat.yml"
      }
    }

    task "prod-task1-packetbeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "docker.elastic.co/beats/packetbeat:${version}"
        dns_servers  = [ "$${attr.unique.network.ip-address}" ]
        privileged   = true
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
        data         = <<EOF
packetbeat.interfaces.device: any
packetbeat.flows:
  enabled: true
  timeout: 30s
  period: 10s
packetbeat.protocols:
- type: icmp
  enabled: true
- type: dhcpv4
  enabled: true
  ports: [67, 68]
- type: dns
  enabled: true
  ports: [53]
  include_authorities: true
  include_additionals: true
- type: http
  enabled: true
  ports: [80, 8080, 8000, 5000, 8002]
- type: tls
  enabled: true
  ports: [443, 8443, 9243]
packetbeat.procs.enabled: false
packetbeat.ignore_outgoing: false
output.elasticsearch:
  enabled: true
  hosts: ["elastic-rest.service.consul:9200"]
  compression_level: 0
  escape_html: true
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  worker: 1
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
setup.kibana:
  host: "kibana.service.consul:5601"
  protocol: "https"
  #username: "elastic"
  #password: "changeme"
  #path: ""
  #space.id: ""
  ssl.enabled: true
  ssl.verification_mode: none
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]
  #ssl.certificate: "/etc/pki/client/cert.pem"
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "/usr/share/packetbeat/packetbeat.yml"
      }
    }
  }
}