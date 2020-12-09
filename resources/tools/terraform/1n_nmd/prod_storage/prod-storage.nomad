job "prod-storage" {
  # The "region" parameter specifies the region in which to execute the job.
  # If omitted, this inherits the default region name of "global".
  # region = "global"
  #
  # The "datacenters" parameter specifies the list of datacenters which should
  # be considered when placing this task. This must be provided.
  datacenters = [ "yul1" ]

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
    max_parallel = 1

    # The "min_healthy_time" parameter specifies the minimum time the allocation
    # must be in the healthy state before it is marked as healthy and unblocks
    # further allocations from being updated.
    min_healthy_time = "10s"

    # The "healthy_deadline" parameter specifies the deadline in which the
    # allocation must be marked as healthy after which the allocation is
    # automatically transitioned to unhealthy. Transitioning to unhealthy will
    # fail the deployment and potentially roll back the job if "auto_revert" is
    # set to true.
    healthy_deadline = "3m"

    # The "progress_deadline" parameter specifies the deadline in which an
    # allocation must be marked as healthy. The deadline begins when the first
    # allocation for the deployment is created and is reset whenever an allocation
    # as part of the deployment transitions to a healthy state. If no allocation
    # transitions to the healthy state before the progress deadline, the
    # deployment is marked as failed.
    progress_deadline = "10m"

    # The "auto_revert" parameter specifies if the job should auto-revert to the
    # last stable job on deployment failure. A job is marked as stable if all the
    # allocations as part of its deployment were marked healthy.
    auto_revert = false

    # The "canary" parameter specifies that changes to the job that would result
    # in destructive updates should create the specified number of canaries
    # without stopping any previous allocations. Once the operator determines the
    # canaries are healthy, they can be promoted which unblocks a rolling update
    # of the remaining allocations at a rate of "max_parallel".
    #
    # Further, setting "canary" equal to the count of the task group allows
    # blue/green deployments. When the job is updated, a full set of the new
    # version is deployed and upon promotion the old version is stopped.
    canary = 1
  }

  # All groups in this job should be scheduled on different hosts.
  constraint {
    operator = "distinct_hosts"
    value    = "true"
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
  group "prod-group1-storage" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count       = 4

    # https://www.nomadproject.io/docs/job-specification/volume
    volume "prod-volume1-storage" {
      type      = "host"
      read_only = false
      source    = "prod-volume-data1-1"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-storage" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      volume_mount {
        volume       = "prod-volume1-storage"
        destination  = "/data/"
        read_only    = false
      }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "minio/minio:RELEASE.2020-12-03T05-49-24Z"
        dns_servers  = [ "${attr.unique.network.ip-address}" ]
        network_mode = "host"
        command      = "server"
        args         = [ "http://10.32.8.1{4...7}:9000/data" ]
        port_map {
          http       = 9000
        }
        privileged   = false
      }

      env {
        MINIO_ACCESS_KEY = "minio"
        MINIO_SECRET_KEY = "minio123"
        MINIO_BROWSER    = "off"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name       = "storage"
        port       = "http"
        tags       = [ "storage${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "Min.io Server HTTP Check Live"
          type     = "http"
          port     = "http"
          protocol = "http"
          method   = "GET"
          path     = "/minio/health/live"
          interval = "10s"
          timeout  = "2s"
          task     = "${TASK}"
        }
        check {
          name     = "Min.io Server HTTP Check Ready"
          type     = "http"
          port     = "http"
          protocol = "http"
          method   = "GET"
          path     = "/minio/health/ready"
          interval = "10s"
          timeout  = "2s"
          task     = "${TASK}"
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
        cpu        = 2000
        memory     = 2048
        network {
          port "http" {
            static = 9000
          }
        }
      }
    }
    task "prod-task2-storage-mgmt" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "minio/mc:RELEASE.2020-12-10T01-26-17Z"
        entrypoint   = [
          "/bin/sh",
          "-c",
          "sleep 80000"
        ]
        dns_servers  = [ "${attr.unique.network.ip-address}" ]
        privileged   = false
        volumes      = [
          "custom/config.json:/config.json",
          "custom/putonly.json:/putonly.json"
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
        data = <<EOH
          {
            "version": "10",
            "aliases": {
              "storage": {
                "url": "http://storage.service.consul:9000",
                "accessKey": "minio",
                "secretKey": "minio123",
                "api": "s3v4",
                "path": "auto"
              }
            }
          }
        EOH
        destination = "custom/config.json"
      }
      template {
        data = <<EOH
          {
            "Statement": [
              {
                "Action": [
                  "s3:PutObject"
                ],
                "Effect": "Allow",
                "Resource": [
                  "arn:aws:s3:::docs.fd.io/*",
                  "arn:aws:s3:::logs.fd.io/*"
                ]
              }
            ],
            "Version": "2012-10-17"
          }
        EOH
        destination = "custom/putonly.json"
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
        cpu         = 500
        memory      = 128
        network {
          mode = "bridge"
        }
      }
    }
  }
}