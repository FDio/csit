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
  type = "service"

  update {
    # The "max_parallel" parameter specifies the maximum number of updates to
    # perform in parallel. In this case, this specifies to update a single task
    # at a time.
    max_parallel = 0

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
    canary = 0
  }

  # All groups in this job should be scheduled on different hosts.
  constraint {
    operator = "distinct_hosts"
    value    = "true"
  }

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
    count = 4

    # Hard coding prefered node as primary.
    affinity {
      attribute = "${attr.unique.hostname}"
      value     = "s46-nomad"
      weight    = 100
    }

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
      driver = "docker"

      volume_mount {
        volume      = "prod-volume1-storage"
        destination = "/data/"
        read_only   = false
      }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image       = "minio/minio:RELEASE.2020-12-03T05-49-24Z"
        dns_servers = [ "${attr.unique.network.ip-address}" ]
        command     = "server"
        args        = [ "/data/" ]
        port_map {
          http      = 9000
        }
        privileged  = false
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
        name       = "Min.io Server HTTP Check"
        port       = "http"
        tags       = [ "storage${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "alive"
          type     = "http"
          port     = "http"
          protocol = "http"
          method   = "GET"
          path     = "/minio/health/live"
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

    task "prod-task2-sync" {
      # The "raw_exec" parameter specifies the task driver that should be used
      # to run the task.
      driver = "raw_exec"

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
        data        = <<EOH
#!/bin/bash

INOTIFY_OPTONS=()
INOTIFY_OPTION+=("--recursive")
INOTIFY_OPTION+=("--monitor")
VOLUMES=()
VOLUMES=("/data/logs.fd.io")
VOLUMES=("/data/docs.fd.io")

if [ '{{ env "attr.unique.network.ip-address" }}' = "10.32.8.14" ]; then
echo "Running notify daemon"
    inotifywait -e moved_to "${INOTIFY_OPTONS[@]}" ${VOLUMES[@]} | \
        while read path action file; do
            key="testuser"
            secret="Csit1234"

            resource=${path#"/data"}${file}
            date=$(date -R)
            _signature="PUT\n\napplication/octet-stream\n${date}\n${resource}"
            signature=$(echo -en ${_signature} | openssl sha1 -hmac ${secret} -binary | base64)

            curl -v -X PUT -T "${path}${file}" \
                -H "Host: storage0.storage.service.consul:9000" \
                -H "Date: ${date}" \
                -H "Content-Type: application/octet-stream" \
                -H "Authorization: AWS ${key}:${signature}" \
                http://storage0.storage.service.consul:9000${resource}
        done
else
    while :; do sleep 2073600; done
fi
EOH
        destination = "local/sync.sh"
        perms       = "744"
      }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        command     = "local/sync.sh"
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
        memory      = 256
      }
    }
  }
}