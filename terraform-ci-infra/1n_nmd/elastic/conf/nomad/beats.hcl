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
    count            = ${group_count}

    restart {
      interval       = "1m"
      attempts       = 3
      delay          = "15s"
      mode           = "delay"
    }

    task "prod-task1-filebeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command      = "local/filebeat-${version}-linux-x86_64/filebeat"
        args         = [
          "-c", "/${data_dir}/filebeat.yml"
        ]
      }

      shutdown_delay = "30s"

      # The artifact stanza instructs Nomad to fetch and unpack a remote
      # resource, such as a file, tarball, or binary. Nomad downloads artifacts
      # using the popular go-getter library, which permits downloading artifacts
      # from a variety of locations using a URL as the input source.
      artifact {
        source       = "https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${version}-linux-x86_64.tar.gz"
        destination  = "${data_dir}"
      }

      template {
        data         = <<EOF
#=========================== Filebeat inputs =============================

# List of inputs to fetch data.
filebeat.inputs:

#------------------------------ Log input --------------------------------
- type: log
  enabled: true

  # Paths that should be crawled and fetched. Glob based paths.
  # To fetch all ".log" files from a specific level of subdirectories
  # /var/log/*/*.log can be used.
  # For each file found under this path, a harvester is started.
  # Make sure not file is defined twice as this can lead to unexpected behaviour.
  paths:
    - /var/log/syslog
    - /var/log/*.log

#------------------------------ Container input --------------------------------
- type: container
  enabled: false

  # Paths that should be crawled and fetched. Glob based paths.
  # To fetch all ".log" files from a specific level of subdirectories
  # /var/log/*/*.log can be used.
  # For each file found under this path, a harvester is started.
  # Make sure not file is defined twice as this can lead to unexpected behaviour.
  paths:
    -/var/lib/docker/containers/*/*.log

  # Configure stream to filter to a specific stream: stdout, stderr or all (default)
  stream: all

# ================================== Outputs ===================================

# Configure what output to use when sending the data collected by the beat.

# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  enabled: true

  # Array of hosts to connect to.
  # Scheme and port can be left out and will be set to the default (http and 9200)
  # In case you specify and additional path, the scheme is required: http://localhost:9200/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:9200
  hosts: ["elasticsearch.service.consul:9200"]

  # Set gzip compression level.
  compression_level: 0

  # Configure escaping HTML symbols in strings.
  escape_html: true

  # Protocol - either `http` (default) or `https`.
  protocol: "https"

  # Authentication credentials - either API key or username/password.
  #api_key: "id:api_key"
  #username: "elastic"
  #password: "changeme"

  # Number of workers per Elasticsearch host.
  worker: 1

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL-based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"

# =================================== Kibana ===================================

# Starting with Beats version 6.0.0, the dashboards are loaded via the Kibana API.
# This requires a Kibana endpoint configuration.
setup.kibana:

  # Kibana Host
  # Scheme and port can be left out and will be set to the default (http and 5601)
  # In case you specify and additional path, the scheme is required: http://localhost:5601/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:5601
  host: "kibana.service.consul:5601"

  # Optional protocol and basic auth credentials.
  #protocol: "https"
  #username: "elastic"
  #password: "changeme"

  # Optional HTTP path
  #path: ""

  # Optional Kibana space ID.
  #space.id: ""

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "${data_dir}/filebeat.yml"
      }
    }

    task "prod-task1-metricbeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command      = "local/metricbeat-${version}-linux-x86_64/metricbeat"
        args         = [
          "-c", "/${data_dir}/metricbeat.yml"
        ]
      }

      shutdown_delay = "30s"

      # The artifact stanza instructs Nomad to fetch and unpack a remote
      # resource, such as a file, tarball, or binary. Nomad downloads artifacts
      # using the popular go-getter library, which permits downloading artifacts
      # from a variety of locations using a URL as the input source.
      artifact {
        source       = "https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-${version}-linux-x86_64.tar.gz"
        destination  = "${data_dir}"
      }

      template {
        data         = <<EOF
#============================  Config Reloading ===============================

# Config reloading allows to dynamically load modules. Each file which is
# monitored must contain one or multiple modules as a list.
metricbeat.config.modules:

  # Glob pattern for configuration reloading
  path: ${path.config}/modules.d/*.yml

  # Period on which files under path should be checked for changes
  reload.period: 10s

  # Set to true to enable config reloading
  reload.enabled: false

# Maximum amount of time to randomly delay the start of a metricset. Use 0 to
# disable startup delay.
metricbeat.max_start_delay: 10s

#==========================  Modules configuration =============================
metricbeat.modules:

#-------------------------------- System Module --------------------------------
- module: system
  metricsets:
    - cpu             # CPU usage
    - load            # CPU load averages
    - memory          # Memory usage
    - network         # Network IO
    - process         # Per process metrics
    - process_summary # Process summary
    - uptime          # System Uptime
    - socket_summary  # Socket summary
    - core            # Per CPU core usage
    - diskio          # Disk IO
    #- filesystem     # File system usage for each mountpoint
    - fsstat         # File system summary metrics
    #- raid           # Raid
    #- socket         # Sockets and connection info (linux only)
    - service        # systemd service information
  enabled: true
  period: 10s
  processes: ['.*']

  # Configure the metric types that are included by these metricsets.
  cpu.metrics:  ["percentages","normalized_percentages"]  # The other available option is ticks.
  core.metrics: ["percentages"]  # The other available option is ticks.

#-------------------------------- Consul Module --------------------------------
- module: consul
  metricsets:
  - agent
  enabled: true
  period: 10s
  hosts: ["localhost:8500"]

#-------------------------------- Docker Module --------------------------------
- module: docker
  metricsets:
    - "container"
    - "cpu"
    - "diskio"
    - "event"
    - "healthcheck"
    - "info"
    #- "image"
    - "memory"
    - "network"
  hosts: ["unix:///var/run/docker.sock"]
  period: 10s
  enabled: true

# ================================== Outputs ===================================

# Configure what output to use when sending the data collected by the beat.

# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  enabled: true

  # Array of hosts to connect to.
  # Scheme and port can be left out and will be set to the default (http and 9200)
  # In case you specify and additional path, the scheme is required: http://localhost:9200/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:9200
  hosts: ["elasticsearch.service.consul:9200"]

  # Set gzip compression level.
  compression_level: 0

  # Configure escaping HTML symbols in strings.
  escape_html: true

  # Protocol - either `http` (default) or `https`.
  protocol: "https"

  # Authentication credentials - either API key or username/password.
  #api_key: "id:api_key"
  #username: "elastic"
  #password: "changeme"

  # Number of workers per Elasticsearch host.
  worker: 1

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL-based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"

# =================================== Kibana ===================================

# Starting with Beats version 6.0.0, the dashboards are loaded via the Kibana API.
# This requires a Kibana endpoint configuration.
setup.kibana:

  # Kibana Host
  # Scheme and port can be left out and will be set to the default (http and 5601)
  # In case you specify and additional path, the scheme is required: http://localhost:5601/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:5601
  host: "kibana.service.consul:5601"

  # Optional protocol and basic auth credentials.
  #protocol: "https"
  #username: "elastic"
  #password: "changeme"

  # Optional HTTP path
  #path: ""

  # Optional Kibana space ID.
  #space.id: ""

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "${data_dir}/metricbeat.yml"
      }
    }

    task "prod-task1-packetbeat" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command      = "local/packetbeat-${version}-linux-x86_64/packetbeat"
        args         = [
          "-c", "/${data_dir}/packetbeat.yml"
        ]
      }

      shutdown_delay = "30s"

      # The artifact stanza instructs Nomad to fetch and unpack a remote
      # resource, such as a file, tarball, or binary. Nomad downloads artifacts
      # using the popular go-getter library, which permits downloading artifacts
      # from a variety of locations using a URL as the input source.
      artifact {
        source       = "https://artifacts.elastic.co/downloads/beats/packetbeat/packetbeat-${version}-linux-x86_64.tar.gz"
        destination  = "${data_dir}"
      }

      template {
        data         = <<EOF
#============================== Network device ================================

# Select the network interface to sniff the data. You can use the "any"
# keyword to sniff on all connected interfaces.
packetbeat.interfaces.device: any

#================================== Flows =====================================

packetbeat.flows:
  enabled: true

  # Set network flow timeout. Flow is killed if no packet is received before being
  # timed out.
  timeout: 30s

  # Configure reporting period. If set to -1, only killed flows will be reported
  period: 10s

#========================== Transaction protocols =============================

packetbeat.protocols:
- type: icmp
  enabled: true

- type: dhcpv4
  enabled: true

  # Configure the DHCP for IPv4 ports.
  ports: [67, 68]

- type: dns
  enabled: true

  # Configure the ports where to listen for DNS traffic. You can disable
  # the DNS protocol by commenting out the list of ports.
  ports: [53]

  # include_authorities controls whether or not the dns.authorities field
  # (authority resource records) is added to messages.
  # Default: false
  include_authorities: true
  # include_additionals controls whether or not the dns.additionals field
  # (additional resource records) is added to messages.
  # Default: false
  include_additionals: true

- type: http
  enabled: true

  # Configure the ports where to listen for HTTP traffic. You can disable
  # the HTTP protocol by commenting out the list of ports.
  ports: [80, 8080, 8000, 5000, 8002]

- type: tls
  enabled: true

  # Configure the ports where to listen for TLS traffic. You can disable
  # the TLS protocol by commenting out the list of ports.
  ports: [443, 8443, 9243]

#=========================== Monitored processes ==============================

# Packetbeat can enrich events with information about the process associated
# the socket that sent or received the packet if Packetbeat is monitoring
# traffic from the host machine. By default process enrichment is disabled.
# This feature works on Linux and Windows.
packetbeat.procs.enabled: false

# If you want to ignore transactions created by the server on which the shipper
# is installed you can enable this option. This option is useful to remove
# duplicates if shippers are installed on multiple servers. Default value is
# false.
packetbeat.ignore_outgoing: false

# ================================== Outputs ===================================

# Configure what output to use when sending the data collected by the beat.

# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  enabled: true

  # Array of hosts to connect to.
  # Scheme and port can be left out and will be set to the default (http and 9200)
  # In case you specify and additional path, the scheme is required: http://localhost:9200/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:9200
  hosts: ["elasticsearch.service.consul:9200"]

  # Set gzip compression level.
  compression_level: 0

  # Configure escaping HTML symbols in strings.
  escape_html: true

  # Protocol - either `http` (default) or `https`.
  protocol: "https"

  # Authentication credentials - either API key or username/password.
  #api_key: "id:api_key"
  #username: "elastic"
  #password: "changeme"

  # Number of workers per Elasticsearch host.
  worker: 1

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL-based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"

# =================================== Kibana ===================================

# Starting with Beats version 6.0.0, the dashboards are loaded via the Kibana API.
# This requires a Kibana endpoint configuration.
setup.kibana:

  # Kibana Host
  # Scheme and port can be left out and will be set to the default (http and 5601)
  # In case you specify and additional path, the scheme is required: http://localhost:5601/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:5601
  host: "kibana.service.consul:5601"

  # Optional protocol and basic auth credentials.
  #protocol: "https"
  #username: "elastic"
  #password: "changeme"

  # Optional HTTP path
  #path: ""

  # Optional Kibana space ID.
  #space.id: ""

  # Use SSL settings for HTTPS.
  ssl.enabled: true

  # Configure SSL verification mode. If `none` is configured, all server hosts
  # and certificates will be accepted. In this mode, SSL based connections are
  # susceptible to man-in-the-middle attacks. Use only for testing. Default is
  # `full`.
  ssl.verification_mode: none

  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client certificate key
  #ssl.key: "/etc/pki/client/cert.key"
EOF
        destination  = "${data_dir}/packetbeat.yml"
      }
    }
  }
}