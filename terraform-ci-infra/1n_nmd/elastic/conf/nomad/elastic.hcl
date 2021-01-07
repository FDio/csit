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

  meta {
    ES_CLUSTER_NAME   = "$${NOMAD_REGION}-$${NOMAD_JOB_NAME}"
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
  group "prod-group1-elastic-cluster" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count             = ${group_count}

    constraint {
      attribute       = "$${node.unique.name}"
      value           = "s41-nomad-x86_64"
    }

    ephemeral_disk {
      size            = "50000"
      sticky          = true
      migrate         = false
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-elastic-cluster" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver          = "docker"

      kill_timeout    = "600s"
      kill_signal     = "SIGTERM"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "docker.elastic.co/elasticsearch/elasticsearch:${version}"
        dns_servers   = [ "$${attr.unique.network.ip-address}" ]
        command       = "elasticsearch"
        args          = [
          "-Ebootstrap.memory_lock=true",
          "-Ecluster.name=$${NOMAD_META_ES_CLUSTER_NAME}",
          "-Ehttp.port=$${NOMAD_PORT_rest}",
          "-Ehttp.publish_port=$${NOMAD_HOST_PORT_rest}",
          "-Enetwork.host=0.0.0.0",
          "-Enetwork.publish_host=0.0.0.0",
          "-Enode.name=$${NOMAD_ALLOC_NAME}",
          "-Epath.logs=/alloc/logs/",
          "-Ediscovery.type=single-node",
          "-Etransport.publish_port=$${NOMAD_HOST_PORT_transport}",
          "-Etransport.port=$${NOMAD_PORT_transport}",
          "-Expack.license.self_generated.type=basic",
          "-Expack.security.enabled=true"
        ]
        ulimit {
          memlock     = "-1"
          nofile      = "65536"
          nproc       = "8192"
        }
#        mounts        = [
#          {
#            type     = "volume"
#            target   = "/usr/share/elasticsearch/data/"
#            source   = "es-cluster-cluster-vol"
#            readonly = false
#          }
#        ]
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name       = "${service_name}-rest"
        port       = "rest"
        tags       = [ "${service_name}-rest$${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "Elastic REST Check Live"
          port     = "rest"
          type     = "tcp"
          interval = "5s"
          timeout  = "4s"
        }
        check {
          name     = "Elastic HTTP Check Live"
          type     = "http"
          port     = "rest"
          path     = "/"
          interval = "5s"
          timeout  = "4s"
        }
      }
      service {
        name       = "${service_name}-transport"
        port       = "transport"
        tags       = [ "${service_name}-transport$${NOMAD_ALLOC_INDEX}" ]
        check {
          name     = "Elastic Transport Check Live"
          type     = "tcp"
          port     = "transport"
          interval = "5s"
          timeout  = "4s"
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
        cpu        = ${cluster_cpu}
        memory     = ${cluster_memory}
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
          port "rest" {
            static = ${cluster_rest_port}
          }
          port "transport" {
            static = ${cluster_transport_port}
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
  group "prod-group1-elastic-kibana" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count              = 1

    constraint {
      attribute        = "$${node.unique.name}"
      value            = "s41-nomad-x86_64"
    }

    update {
      max_parallel     = 1
      health_check     = "checks"
      min_healthy_time = "10s"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-elastic-task" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver           = "docker"

      kill_timeout     = "60s"
      kill_signal      = "SIGTERM"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image         = "docker.elastic.co/kibana/kibana:${version}"
        dns_servers   = [ "$${attr.unique.network.ip-address}" ]
        command       = "kibana"
        args          = [
          "--elasticsearch.hosts=http://$${NOMAD_IP_http}:9200",
          "--server.host=0.0.0.0",
          "--server.name=$${NOMAD_JOB_NAME}",
          "--server.port=$${NOMAD_PORT_http}",
          "--xpack.apm.ui.enabled=false",
          "--xpack.graph.enabled=false",
          "--xpack.grokdebugger.enabled=false",
          "--xpack.maps.enabled=false",
          "--xpack.ml.enabled=false",
          "--xpack.searchprofiler.enabled=false"
        ]
        ulimit {
          memlock = "-1"
          nofile = "65536"
          nproc = "8192"
        }
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name       = "${service_name}-kibana"
        port       = "http"
        check {
          name     = "Elastic Kibana Transport Check Live"
          port     = "http"
          type     = "tcp"
          interval = "5s"
          timeout  = "4s"
        }
        check {
          name     = "Elastic Kibana HTTP Check Live"
          type     = "http"
          port     = "http"
          path     = "/"
          interval = "5s"
          timeout  = "4s"
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
        cpu        = ${kibana_cpu}
        memory     = ${kibana_memory}
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
          port "http" {
            static = ${kibana_port}
          }
        }
      }
    }
  }
}
