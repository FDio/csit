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

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-csit-shim-amd" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count            = ${group_count}

    constraint {
      attribute      = "$${node.class}"
      value          = "csit"
    }

    restart {
      interval       = "1m"
      attempts       = 3
      delay          = "15s"
      mode           = "delay"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-csit-shim-amd" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "${image_x86_64}"
        network_mode = "host"
        pid_mode     = "host"
        volumes      = [
          "/var/run/docker.sock:/var/run/docker.sock"
        ]
        privileged   = true
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
        cpu          = ${cpu}
        memory       = ${mem}
        network {
          port "ssh" {
              static = 6022
          }
          port "ssh2" {
              static = 6023
          }
        }
      }
    }
  }

  group "prod-group1-csit-shim-arm" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count            = ${group_count}

    constraint {
      attribute      = "$${node.class}"
      value          = "csitarm"
    }

    restart {
      interval       = "1m"
      attempts       = 3
      delay          = "15s"
      mode           = "delay"
    }

    # The "task" stanza creates an individual unit of work, such as a Docker
    # container, web application, or batch processing.
    #
    # For more information and examples on the "task" stanza, please see
    # the online documentation at:
    #
    #     https://www.nomadproject.io/docs/job-specification/task.html
    #
    task "prod-task1-csit-shim-arm" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver         = "docker"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "${image_aarch64}"
        network_mode = "host"
        pid_mode     = "host"
        volumes      = [
          "/var/run/docker.sock:/var/run/docker.sock"
        ]
        privileged   = true
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
        cpu          = ${cpu}
        memory       = ${mem}
        network {
          port "ssh" {
              static = 6022
          }
          port "ssh2" {
              static = 6023
          }
        }
      }
    }
  }
}