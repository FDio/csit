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
  type        = "batch"

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-mc" {
    task "prod-task1-create-buckets" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver        = "docker"

      %{ if use_vault_provider }
      vault {
        policies    = "${vault_kv_policy_name}"
      }
     %{ endif }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image       = "${image}"
        entrypoint  = [
          "/bin/sh",
          "-c",
          "${command}"
        ]
        dns_servers  = [ "$${attr.unique.network.ip-address}" ]
        privileged   = false
      }

      # The env stanza configures a list of environment variables to populate
      # the task's environment before starting.
      env {
        %{ if use_vault_provider }
        {{ with secret "${vault_kv_path}" }}
        MINIO_ACCESS_KEY = "{{ .Data.data.${vault_kv_field_access_key} }}"
        MINIO_SECRET_KEY = "{{ .Data.data.${vault_kv_field_secret_key} }}"
        {{ end }}
        %{ else }
        MINIO_ACCESS_KEY = "${access_key}"
        MINIO_SECRET_KEY = "${secret_key}"
        %{ endif }
        ${ envs }
      }
    }
  }
}
