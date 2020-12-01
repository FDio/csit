job "prod-nginx" {
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

  # The "group" stanza defines a series of tasks that should be co-located on
  # the same Nomad client. Any task within a group will be placed on the same
  # client.
  #
  # For more information and examples on the "group" stanza, please see
  # the online documentation at:
  #
  #     https://www.nomadproject.io/docs/job-specification/group.html
  #
  group "prod-group1-nginx" {
    # The "count" parameter specifies the number of the task groups that should
    # be running under this group. This value must be non-negative and defaults
    # to 1.
    count = 1

    # All groups in this job should be scheduled on different hosts.
    constraint {
      operator  = "distinct_hosts"
      value     = "false"
    }

    # Prioritize one node.
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
    task "prod-task1-nginx" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver = "docker"

      volume_mount {
        volume      = "prod-volume1-storage"
        destination = "/data/"
        read_only   = true
      }

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.
      config {
        image        = "nginx:stable"
        dns_servers  = [ "${attr.unique.network.ip-address}" ]
        port_map {
          https      = 443
        }
        privileged   = false
        volumes      = [
          "/etc/consul.d/ssl/consul.pem:/etc/ssl/certs/nginx-cert.pem",
          "/etc/consul.d/ssl/consul-key.pem:/etc/ssl/private/nginx-key.pem",
          "custom/logs.conf:/etc/nginx/conf.d/logs.conf",
          "custom/docs.conf:/etc/nginx/conf.d/docs.conf"
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
          server {
            listen 443 ssl default_server;
            server_name logs.nginx.service.consul;
            keepalive_timeout 70;
            ssl_session_cache shared:SSL:10m;
            ssl_session_timeout 10m;
            ssl_protocols TLSv1.2;
            ssl_prefer_server_ciphers on;
            ssl_ciphers "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384";
            ssl_certificate /etc/ssl/certs/nginx-cert.pem;
            ssl_certificate_key /etc/ssl/private/nginx-key.pem;
            location / {
              root /data/logs.fd.io;
              index _;
              autoindex on;
              autoindex_exact_size on;
              autoindex_format html;
              autoindex_localtime off;
            }
            location ~ \.(html.gz)$ {
              root /data/logs.fd.io;
              add_header Content-Encoding gzip;
              add_header Content-Type text/html;
            }
            location ~ \.(txt.gz|log.gz)$ {
              root /data/logs.fd.io;
              add_header Content-Encoding gzip;
              add_header Content-Type text/plain;
            }
            location ~ \.(xml.gz)$ {
              root /data/logs.fd.io;
              add_header Content-Encoding gzip;
              add_header Content-Type application/xml;
            }
          }
        EOH
        destination = "custom/logs.conf"
      }
      template {
        data = <<EOH
          server {
            listen 443 ssl;
            server_name docs.nginx.service.consul;
  	        keepalive_timeout 70;
  	        ssl_session_cache shared:SSL:10m;
          	ssl_session_timeout 10m;
  	        ssl_protocols TLSv1.2;
	          ssl_prefer_server_ciphers on;
  	        ssl_ciphers "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384";
            ssl_certificate /etc/ssl/certs/nginx-cert.pem;
            ssl_certificate_key /etc/ssl/private/nginx-key.pem;
            location / {
              root /data/docs.fd.io;
              index index.html index.htm;
            }
          }
        EOH
        destination = "custom/docs.conf"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name       = "nginx"
        port       = "https"
        tags       = [ "docs", "logs" ]
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
        cpu        = 1000
        memory     = 1024
        network {
          mode     = "bridge"
          port "https" {
            static = 443
          }
        }
      }
    }
  }
}