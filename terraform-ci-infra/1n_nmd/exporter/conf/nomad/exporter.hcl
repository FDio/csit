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
  #     https://www.nomadproject.io/docs/jobspec/schedulers
  #
  type                = "system"

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
  #     https://www.nomadproject.io/docs/job-specification/group
  #
  group "prod-group1-exporter-amd64" {
    # The constraint allows restricting the set of eligible nodes. Constraints
    # may filter on attributes or client metadata.
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
    #     https://www.nomadproject.io/docs/job-specification/task
    #
    task "prod-task1-${node_service_name}-amd64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "raw_exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command       = "local/node_exporter-${node_version}.linux-amd64/node_exporter"
      }

      # The artifact stanza instructs Nomad to fetch and unpack a remote resource,
      # such as a file, tarball, or binary. Nomad downloads artifacts using the
      # popular go-getter library, which permits downloading artifacts from a
      # variety of locations using a URL as the input source.
      #
      #     https://www.nomadproject.io/docs/job-specification/artifact
      #
      artifact {
        source        = "${node_url_amd64}"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${node_service_name}"
        port          = "${node_service_name}"
        check {
          name        = "Node Exporter Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${node_service_name}" {
            static    = ${node_port}
          }
        }
      }
    }
    task "prod-task2-${blackbox_service_name}-amd64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command       = "local/blackbox_exporter-${blackbox_version}.linux-amd64/blackbox_exporter"
        args          = [
          "--config.file=secrets/blackbox.yml"
        ]
      }

      # The "template" stanza instructs Nomad to manage a template, such as
      # a configuration file or script. This template can optionally pull data
      # from Consul or Vault to populate runtime configuration data.
      #
      #     https://www.nomadproject.io/docs/job-specification/template
      #
      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/blackbox.yml"
        data            = <<EOH
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      no_follow_redirects: false
      fail_if_ssl: false
      fail_if_not_ssl: true
      tls_config:
        insecure_skip_verify: false
      preferred_ip_protocol: "ip4"
  icmp_v4:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
  dns_udp:
    prober: dns
    timeout: 5s
    dns:
      query_name: "jenkins.fd.io"
      query_type: "A"
      valid_rcodes:
      - NOERROR
EOH
      }

      # The artifact stanza instructs Nomad to fetch and unpack a remote resource,
      # such as a file, tarball, or binary. Nomad downloads artifacts using the
      # popular go-getter library, which permits downloading artifacts from a
      # variety of locations using a URL as the input source.
      #
      #     https://www.nomadproject.io/docs/job-specification/artifact
      #
      artifact {
        source        = "${blackbox_url_amd64}"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${blackbox_service_name}"
        port          = "${blackbox_service_name}"
        tags          = [ "${blackbox_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name        = "Blackbox Exporter Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${blackbox_service_name}" {
            static    = ${blackbox_port}
          }
        }
      }
    }

    task "prod-task3-${cadvisor_service_name}-amd64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "${cadvisor_image}"
        volumes       = [
          "/:/rootfs:ro",
          "/var/run:/var/run:rw",
          "/sys:/sys:ro",
          "/var/lib/docker/:/var/lib/docker:ro",
          "/cgroup:/cgroup:ro"
        ]
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${cadvisor_service_name}"
        port          = "${cadvisor_service_name}"
        check {
          name        = "cAdvisor Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${cadvisor_service_name}" {
            static    = ${cadvisor_port}
          }
        }
      }
    }
  }

  group "prod-group1-exporter-arm64" {
    # The constraint allows restricting the set of eligible nodes. Constraints
    # may filter on attributes or client metadata.
    #
    #     https://www.nomadproject.io/docs/job-specification/constraint
    #
    constraint {
      attribute       = "$${attr.cpu.arch}"
      operator        = "=="
      value           = "arm64"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    #     https://www.nomadproject.io/docs/job-specification/task
    #
    task "prod-task1-${node_service_name}-arm64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "raw_exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command       = "local/node_exporter-${node_version}.linux-arm64/node_exporter"
      }

      # The artifact stanza instructs Nomad to fetch and unpack a remote resource,
      # such as a file, tarball, or binary. Nomad downloads artifacts using the
      # popular go-getter library, which permits downloading artifacts from a
      # variety of locations using a URL as the input source.
      #
      #     https://www.nomadproject.io/docs/job-specification/artifact
      #
      artifact {
        source        = "${node_url_arm64}"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${node_service_name}"
        port          = "${node_service_name}"
        check {
          name        = "Node Exporter Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${node_service_name}" {
            static    = ${node_port}
          }
        }
      }
    }

    task "prod-task2-${blackbox_service_name}-arm64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command       = "local/blackbox_exporter-${blackbox_version}.linux-arm64/blackbox_exporter"
        args          = [
          "--config.file=secrets/blackbox.yml"
        ]
      }

      # The "template" stanza instructs Nomad to manage a template, such as
      # a configuration file or script. This template can optionally pull data
      # from Consul or Vault to populate runtime configuration data.
      #
      #     https://www.nomadproject.io/docs/job-specification/template
      #
      template {
        change_mode     = "noop"
        change_signal   = "SIGINT"
        destination     = "secrets/blackbox.yml"
        data            = <<EOH
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      no_follow_redirects: false
      fail_if_ssl: false
      fail_if_not_ssl: true
      tls_config:
        insecure_skip_verify: false
      preferred_ip_protocol: "ip4"
  icmp_v4:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
  dns_udp:
    prober: dns
    timeout: 5s
    dns:
      query_name: "jenkins.fd.io"
      query_type: "A"
      valid_rcodes:
      - NOERROR
EOH
      }

      # The artifact stanza instructs Nomad to fetch and unpack a remote resource,
      # such as a file, tarball, or binary. Nomad downloads artifacts using the
      # popular go-getter library, which permits downloading artifacts from a
      # variety of locations using a URL as the input source.
      #
      #     https://www.nomadproject.io/docs/job-specification/artifact
      #
      artifact {
        source        = "${blackbox_url_arm64}"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${blackbox_service_name}"
        port          = "${blackbox_service_name}"
        tags          = [ "${blackbox_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name        = "Blackbox Exporter Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${blackbox_service_name}" {
            static    = ${blackbox_port}
          }
        }
      }
    }

    task "prod-task3-${cadvisor_service_name}-arm64" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        # There is currently no official release for arm yet...using community.
        image         = "zcube/cadvisor:latest"
        volumes       = [
          "/:/rootfs:ro",
          "/var/run:/var/run:rw",
          "/sys:/sys:ro",
          "/var/lib/docker/:/var/lib/docker:ro",
          "/cgroup:/cgroup:ro"
        ]
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      #     https://www.nomadproject.io/docs/job-specification/service
      #
      service {
        name          = "${cadvisor_service_name}"
        port          = "${cadvisor_service_name}"
        check {
          name        = "cAdvisor Check Live"
          type        = "http"
          path        = "/metrics"
          interval    = "10s"
          timeout     = "2s"
        }
      }

      # The "resources" stanza describes the requirements a task needs to
      # execute. Resource requirements include memory, network, cpu, and more.
      # This ensures the task will execute on a machine that contains enough
      # resource capacity.
      #
      #     https://www.nomadproject.io/docs/job-specification/resources
      #
      resources {
        cpu           = 500
        # The network stanza specifies the networking requirements for the task
        # group, including the network mode and port allocations. When scheduling
        # jobs in Nomad they are provisioned across your fleet of machines along
        # with other jobs and services. Because you don't know in advance what host
        # your job will be provisioned on, Nomad will provide your tasks with
        # network configuration when they start up.
        #
        #     https://www.nomadproject.io/docs/job-specification/network
        #
        network {
          port "${cadvisor_service_name}" {
            static    = ${cadvisor_port}
          }
        }
      }
    }
  }
}