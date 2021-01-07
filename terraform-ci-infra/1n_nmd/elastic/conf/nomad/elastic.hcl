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
          "-Enode.name=${cluster_service_name}$${NOMAD_ALLOC_INDEX}",
          "-Enetwork.host=0.0.0.0",
          "-Ecluster.name=${cluster_service_name}",
          "-Ehttp.port=$${NOMAD_PORT_rest}",
          "-Ehttp.publish_port=$${NOMAD_HOST_PORT_rest}",
          "-Ebootstrap.memory_lock=true",
          "-Epath.logs=/alloc/logs/",
          "-Ediscovery.type=single-node",
          "-Etransport.publish_port=$${NOMAD_HOST_PORT_transport}",
          "-Etransport.port=$${NOMAD_PORT_transport}",
          "-Expack.license.self_generated.type=basic",
          "-Expack.security.enabled=true",
          "-Expack.security.http.ssl.enabled=true",
          "-Expack.security.http.ssl.key=certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key",
          "-Expack.security.http.ssl.certificate=certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt",
          "-Expack.security.http.ssl.certificate_authorities=certs/ca.crt",
          "-Expack.security.transport.ssl.enabled=true",
          "-Expack.security.transport.ssl.key=certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key",
          "-Expack.security.transport.ssl.certificate=certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt",
          "-Expack.security.transport.ssl.certificate_authorities=certs/ca.crt",
          "-Expack.security.transport.ssl.verification_mode=certificate"
        ]
        volumes       = [
          "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt:/usr/share/elasticsearch/config/certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt",
          "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key:/usr/share/elasticsearch/config/certs/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key",
          "secrets/ca.crt:/usr/share/elasticsearch/config/certs/ca.crt",
          "secrets/ca.key:/usr/share/elasticsearch/config/certs/ca.key",
          "secrets/password:/usr/share/elasticsearch/config/password"
        ]
        ulimit {
          memlock     = "-1"
          nofile      = "65536"
          nproc       = "8192"
        }
      }

      # The env stanza configures a list of environment variables to populate
      # the task's environment before starting.
      env {
        ELASTIC_PASSWORD       = "${cluster_password}"
#        ELASTIC_PASSWORD_FILE  = "/usr/share/elasticsearch/config/password"
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
${cluster_password}
EOF
        destination  = "secrets/password"
        perms        = "600"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDRjCCAi6gAwIBAgIUKHjku5RBb4UD9nm+Fg2RxR3z5mIwDQYJKoZIhvcNAQEL
BQAwNDEyMDAGA1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5l
cmF0ZWQgQ0EwHhcNMjEwMTEzMDg0MDQ2WhcNMjQwMTEzMDg0MDQ2WjATMREwDwYD
VQQDEwhlbGFzdGljMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMtu
BC5mFsyuq8RsaRpd8KyRaOPdRxqLiqLUONcc76XtvyGQT/87av2l5cuzniT/QZ0s
VRpMeZWoRLF1SWS6YCCi+ohnaSun0tWXBdE5fdLv6yuNosAxgD7moIRSjSQ1loKm
ZEM6m0csVG/sh5J4J2APcJJjKPdOCf2szl/4Ct4VbutCaBex7E3ZmB2T1/adHh9F
OkGZYj5FntsDL5eycYKmWOVDf/j24AMlCWzuucdZ/H0XZQ8OKou/Ut8v7hh5w2FT
11/5uw/1C2Q4iVJnBWL6BADtxef0f6kCg3epXo35IIsmKpKecnW377kaO348SFmd
BsIlPcCUUgXDQs/pJ+UCAwEAAaNxMG8wHQYDVR0OBBYEFCDsjcPITceLLpr2U8Xj
cYLkKh6vMB8GA1UdIwQYMBaAFJkrC2lnfFdDaGNb7KPRhGy8tvw1MCIGA1UdEQQb
MBmCF2VsYXN0aWMxLnNlcnZpY2UuY29uc3VsMAkGA1UdEwQCMAAwDQYJKoZIhvcN
AQELBQADggEBADkT03usfJNn5G2Ldq9UBb2D5WTzcZ+OXdqcH1iTT8+0SwnqVvro
DO2aE98XLqK/v2mlmU9ohrEsxhJAAHzc0wmL+kHk98z5EKAkXjj7hLtEyaTWLFGH
V+Z1Oi+kTjukEDbHt2IP8/8HibjEWXqqbhFVQqmdON9axTtyO6syEonjBeLEO/89
6Ki9GFmHKJp6WCpzRg0i5a1stPTo5cE+QJUiJjx5WmCXocakAAdORS3ES6gRYKW5
KdD5AOlR6NNaewCZh0lNjZ3SmUUzSZ+HDJXi+BE4k1PJbyQ8Lav7rq5MXHtnV4kX
4SC56vJ0z2g7/SonGTOJGWAbPGm6oK6Cu64=
-----END CERTIFICATE-----
EOF
        destination  = "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAy24ELmYWzK6rxGxpGl3wrJFo491HGouKotQ41xzvpe2/IZBP
/ztq/aXly7OeJP9BnSxVGkx5lahEsXVJZLpgIKL6iGdpK6fS1ZcF0Tl90u/rK42i
wDGAPuaghFKNJDWWgqZkQzqbRyxUb+yHkngnYA9wkmMo904J/azOX/gK3hVu60Jo
F7HsTdmYHZPX9p0eH0U6QZliPkWe2wMvl7JxgqZY5UN/+PbgAyUJbO65x1n8fRdl
Dw4qi79S3y/uGHnDYVPXX/m7D/ULZDiJUmcFYvoEAO3F5/R/qQKDd6lejfkgiyYq
kp5ydbfvuRo7fjxIWZ0GwiU9wJRSBcNCz+kn5QIDAQABAoIBAQCmz7QGCBiyBpk7
HFqjEF0GZMZJ820Wy04Hb1acrlGlEmskLp4qgKKfE6Z3fvYzCEzZgTzXr9YTbkPF
8JMaUen5WStvJr0K2zb7hjdy9V3D1pBUynOmffDXo24Ek1zBUF/3ClI0/p3NowAq
Nx6EcJp5HrAEmeNBx3BR353q/A6NRDd3/hbnZi+SfySI6eT4IfelKzhDSbjeuJwY
ysIukB6EBpJmhY7Zh9aK5QfPLA4hNyiLu04IhnwRkRh2s8G1Yckfdr/O3JmL+W1E
rbNYF1Nxbr3aU22JFzoe1H2uSvaeQYzk2SNMCGhrF84hmyPXctp34Ao+H/dVBZZc
4heI+G2BAoGBAO3MMzJmami4keA3Lo4N7i1jYQun+heTM0m43M/QKqICy/Rp/g6M
ChedNyRTUHWIsnt8QUz9L1HLHKuYmyfiKfdkt06uVDsQK4lbzbjsoCe0DYnxkXhE
o+mW5nUzRz2DL0orM7VZT64KVtTrTFtoxjm0pyGm0ayASOSPY9wHl5cZAoGBANsA
WtfXSc4yt11QSkd6tGQdRCw+kcMXhiI2aRbtTha0yComXRo8SNXzvIfE5tIZ2oFG
e2Kc1YHOPCEhq884ODbW8N+iBQnRst1yhM34Fc/TsFzTMuEGDXqyyRbPNn1MmkMI
SSf4cmW9LhvE3Iph6jSgYB1nMRcptd6/+pS/NeytAoGAR8cpdP8hA3ci4TEG5m4i
BKVIt8H+ZXtTMd+RF1FYbQq3EZGk1DNFIJed+2MCmFeouElrVJff3qqWft1TiBhm
XnySMDfCyQk6ev2w/S6/sPxSUd8O7+SYLXwVGC9gQ5sDfTnJI+ZPfNM2HpLfu3/G
xchX4np+M7mNRyBZHiNUiJECgYEAhjDAeTMMoVFIM+BHs2bHc/TO2gF41T7rzLjk
Sc0cpSMe51zcfX/k7VxM8DBBcwmubroeTn1lAgW5qF92ZCHBqDCqJY2kYrDgVXqf
T4ms68x9a1NqAKHxznYQa26Kp9oxR9Oi59//UMHLp+5HaG+4z4hZfIrHdLb1Hskp
pM1JIH0CgYAwoIef0P/STykVI+YqK+06sEsEMjFPSg72fLimydSIAjMLc1xvnJYm
4YnyNVtIqP4LmgQ3vKnz5yzHpsTWEeUAZ2d7UHE1gC5ZpV4DZvZIEzfPLU+cuQ+C
pFg9P7CZoeBBAHzVURVcinBkME7b+7RD5YkgJUr3+9KrSlisUMdvFg==
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDSjCCAjKgAwIBAgIVANfV55rdCci2edv4n6+zvIQ+TxWoMA0GCSqGSIb3DQEB
CwUAMDQxMjAwBgNVBAMTKUVsYXN0aWMgQ2VydGlmaWNhdGUgVG9vbCBBdXRvZ2Vu
ZXJhdGVkIENBMB4XDTIxMDExMzA4NDA0NloXDTI0MDExMzA4NDA0NlowNDEyMDAG
A1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5lcmF0ZWQgQ0Ew
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCKgXUkoslTKKVeDMsfR9wW
/jcT1ap576/BXrXK4LHgD8Cd2yGoQkS7aswln5KGM2X6k7qRGN6zMJuZq7yN88dP
FVmU8/r8fKfhbhpwpus0Y3NyziSTIcZRoendx3I1jktEDcFFcB1yoVdbClh6S4Z+
MkxHhCwBATvCCmNrwISbLLGyfYkmO10PW8zD/ly1UkSZJ//xfLBtL1u34Q5Aw38r
eBzxBIZRP5hBwnMXUiGo8Kz6ugJ+Qu7YbVL8z1Ie7icIsgjH8mulR23FZjEb5SXm
0sVchA2vDLPkzdJCI8oDgrbT2KBSkr4u+wuo6VDDQsLWaI+uPhULHwdGQUVinliT
AgMBAAGjUzBRMB0GA1UdDgQWBBSZKwtpZ3xXQ2hjW+yj0YRsvLb8NTAfBgNVHSME
GDAWgBSZKwtpZ3xXQ2hjW+yj0YRsvLb8NTAPBgNVHRMBAf8EBTADAQH/MA0GCSqG
SIb3DQEBCwUAA4IBAQBI9jkC3/B2SYc0v/uIS4AZ/7zvLi/bH+D2PsI9+Rhm7ae5
rqXlN2eG8xdTKi4WTKLHOESJWeY5NSK6wAT5CPr1gfByzDAfFbnrwTtz4ELnAiw9
Z4yTU/0ticQ4/d4vJXUPWZ8vqKCi6oTemPhdX0QoO65TKWYZRaaIPgKox+Q4VUP9
LIUT7NBJn+Z5j+Bbyse0dQwzbKhUEOuQOfMcj7pyKFGeqVUEpRdbpEQ70hlHkwZ7
Hon4+ZsQ95BgCpPCm1rHSy/sJgiJ971CmwVJO8TjBgd4iwCit4x+EcFWsVUra/g0
+FKz2L0enirRpzXpG4aNI/bSpiR3yLxAMENFkpo0
-----END CERTIFICATE-----
EOF
        destination  = "secrets/ca.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAioF1JKLJUyilXgzLH0fcFv43E9Wqee+vwV61yuCx4A/Andsh
qEJEu2rMJZ+ShjNl+pO6kRjeszCbmau8jfPHTxVZlPP6/Hyn4W4acKbrNGNzcs4k
kyHGUaHp3cdyNY5LRA3BRXAdcqFXWwpYekuGfjJMR4QsAQE7wgpja8CEmyyxsn2J
JjtdD1vMw/5ctVJEmSf/8XywbS9bt+EOQMN/K3gc8QSGUT+YQcJzF1IhqPCs+roC
fkLu2G1S/M9SHu4nCLIIx/JrpUdtxWYxG+Ul5tLFXIQNrwyz5M3SQiPKA4K209ig
UpK+LvsLqOlQw0LC1miPrj4VCx8HRkFFYp5YkwIDAQABAoIBAQCKDA3dvgI7SD/K
RaYOP2k14Zqzwjpv3l2mtecrllizof+xVj9tnN80jXV76lf4OjJiVeuVwtv0bXYo
6+q68Uato/HtbF+0V+pb3YmszjGPva/LtXruyrMHmgGmcqt6haCu66a+tsgjAHw4
2U7mVXBvR2KPxUS2m6wb8o61TuTcY3ATcYb05DN03nB42P6pDt/GVd1QrbKLylOT
Hopsr1ApgxvhPnxC90hgz4wniDI2RYhUgQbasNeC6CuSgjlQVCTl44JUIy/gQf0A
rLX1lEySapHbLr8oxKpkvmfCh519vc9RnFjBIwzO3SAmNRUduZj+XFYJPgeavOjD
5qYI88oBAoGBAMHjNew5mwqxAIjekKoJadv+Qz/xwwU+KA63GrDHqPfrs/4WJHJ7
O0z5xFE5ANMYtC1EIxDfnZ4i3ZlPN3LpdzwPz6veAjUCHYNcf4USvErvawBluHbj
negkbjm7FyzVsyYNfkRk8pUrV4Pbw/eb2+mMeAOBCnuFBL8wWxYDzuUhAoGBALbg
XGwU/zoYzq/xTkChojSJwKXjJovTFNkRgl6OyxdgjIKKogH1e0xYzGLuIk0olUwI
8xP/77VGqnnE/dFnQ3pX0g7wgDwkXRBONnC0z21cNa5uB5cUKFUi4en61u/eORzF
DZjLf4+QQD0CtU9MRz/okQ82LxzkLSR/D4BLfVMzAoGBAKcocrbku0yuaZ2W9PYE
A6ZNQkGA9/gvLG3zYymCGaUVKysmf+nLYMbul1jHYnSc2cok8m57u/I4cQDaER4b
Nlcr8olkcFavKi60sqRSENAyNfgzuqOVffBEaFuRd1uKKlfmTjQ9K/97TIo8EGoL
j799AYNT32u6tOr4j68dPWTBAoGBAK1iJF4Yvi6fzH5FYzKlzDrRi8P7i9UvqGlx
T1BFQ8oDMNSniZgf3Olymz0El6Ld4ka3iXchxWvx9rkCir7Zj8FTuAWQAZSDyXQn
IzhSRQNjVEXvbeTQKLknHFeRCe1bnHxpW03NSkCbvDvb8HihUkAGSFnKvno+34nl
qZWyfLy/AoGAaonDtHmKHmhNZF35M6LQ81VmWRLw62LeYIdOCE+9PBMQgM8EtJ1Z
5+F32dIDaP8QCkgYV7AyE1sxQvjYISu5OK2EEyl4aLYm9K0P1eeK6HEXz1HYkZpt
NdZ6+3q7IGzxoqkmJmoR0bjrAZXH3mTEIsWZJTIK7qM+TM02GL8CHSg=
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/ca.key"

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
        name              = "${cluster_service_name}"
        port              = "rest"
        tags              = [ "${cluster_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Elastic Cluster REST Check Live"
          port            = "rest"
          type            = "tcp"
          interval        = "5s"
          timeout         = "4s"
        }
        check {
          name            = "Elastic Cluster HTTP Check Live"
          type            = "http"
          port            = "rest"
          protocol        = "https"
          method          = "GET"
          header {
            Authorization = ["Basic ZWxhc3RpYzpFbGFzdGljMTIzNA=="]
          }
          tls_skip_verify = true
          path            = "/_cluster/health?pretty"
          interval        = "5s"
          timeout         = "4s"
        }
      }
      service {
        name              = "${cluster_service_name}-transport"
        port              = "transport"
        tags              = [ "${cluster_service_name}-transport$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Elastic Cluster Transport Check Live"
          type            = "tcp"
          port            = "transport"
          interval        = "5s"
          timeout         = "4s"
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
          "--server.name=${kibana_service_name}",
          "--server.host=0.0.0.0",
          "--server.port=$${NOMAD_PORT_http}",
          "--server.ssl.enabled=true",
          "--server.ssl.certificate=/etc/kibana/config/certs/${kibana_service_name}.crt",
          "--server.ssl.key=/etc/kibana/config/certs/${kibana_service_name}.key",
          "--elasticsearch.hosts=http://${cluster_service_name}.service.consul:9200",
          "--elasticsearch.username=kibanauser",
          "--elasticsearch.password=Kibana1234",
          "--elasticsearch.ssl.certificateAuthorities=/etc/kibana/config/certs/ca.crt",
          "--xpack.apm.ui.enabled=false",
          "--xpack.graph.enabled=false",
          "--xpack.grokdebugger.enabled=false",
          "--xpack.maps.enabled=false",
          "--xpack.ml.enabled=false",
          "--xpack.searchprofiler.enabled=false"
        ]
        volumes       = [
          "secrets/${kibana_service_name}.crt:/etc/kibana/config/certs/${kibana_service_name}.crt",
          "secrets/${kibana_service_name}.key:/etc/kibana/config/certs/${kibana_service_name}.key",
          "secrets/ca.crt:/etc/kibana/config/certs/ca.crt",
          "secrets/ca.key:/etc/kibana/config/certs/ca.key"
        ]
        ulimit {
          memlock     = "-1"
          nofile      = "65536"
          nproc       = "8192"
        }
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
-----BEGIN CERTIFICATE-----
MIIDQjCCAiqgAwIBAgIULmIAn3JK6TSHotfL1HexLzHBz60wDQYJKoZIhvcNAQEL
BQAwNDEyMDAGA1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5l
cmF0ZWQgQ0EwHhcNMjEwMTEzMDg0MDQ2WhcNMjQwMTEzMDg0MDQ2WjARMQ8wDQYD
VQQDEwZraWJhbmEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCGwE7u
MO7RfEjfcvtnthZvLfBxEW/CbMfaHa6P2VdmSOi6AYIMZBkYfMEzGJDK8p/lDahm
aXyHc9/Lc+cA0H2XLVgBGZERJirdz3zKkqHLa+BcQxighDJJ3a9zsABoXALsxNgK
iCuFyrOQEEKkM775ZyrdQ6RE39KZLB3GMzkbCRQ/A3HTox8uzgoiXLLvNK60TIgb
7Sg9v/Zt2ZrFkQu0TsSGouYtYPgvdf9osRznP4QX511HjXV+/P/0Q1abmJU5/WZd
Dk0Sd4TmfscuOiizmO8mrOG2afN4Gc+VYkNzLMVn92DGz/WxP3dKhIhfMyMCqj5M
JNlCCvVaNm/wujR7AgMBAAGjbzBtMB0GA1UdDgQWBBQKzxXjr7QlQfEdLDo2dNup
oJQKYzAfBgNVHSMEGDAWgBSZKwtpZ3xXQ2hjW+yj0YRsvLb8NTAgBgNVHREEGTAX
ghVraWJhbmEuc2VydmljZS5jb25zdWwwCQYDVR0TBAIwADANBgkqhkiG9w0BAQsF
AAOCAQEAW1h8U2s4RQoJnbmQOIJYcn8b9+glmOVq09ch5knc22C6VOPaSTUyAMkM
3glrPnfbvFmSYGNTzXRkZ0m3GI0QSaiVZ8jHQq0unk904+zEqaxT1gMFKc3iv1lP
DGxMWemP3T9FsEN6Ll9N5YSXP+IonwMEW8mh3PDWDkNZ4haYtbzFyDSNIawljU7G
n/oqIX0bk7gTaqW789L4GDYWhP1vDldkLBhZOiBIrByaIfHvdYFmhfrXiDMKhkXJ
6UJ4tFnU8c0xjVk9/uGCuwaUvaweBp9yJQGIknWlH8O/59JjcX7n1/GkGSAtwkH0
/M+PDfjDTL3FtqY8MYHnkjVItwzftQ==
-----END CERTIFICATE-----
EOF
        destination  = "secrets/${kibana_service_name}.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAhsBO7jDu0XxI33L7Z7YWby3wcRFvwmzH2h2uj9lXZkjougGC
DGQZGHzBMxiQyvKf5Q2oZml8h3Pfy3PnANB9ly1YARmRESYq3c98ypKhy2vgXEMY
oIQySd2vc7AAaFwC7MTYCogrhcqzkBBCpDO++Wcq3UOkRN/SmSwdxjM5GwkUPwNx
06MfLs4KIlyy7zSutEyIG+0oPb/2bdmaxZELtE7EhqLmLWD4L3X/aLEc5z+EF+dd
R411fvz/9ENWm5iVOf1mXQ5NEneE5n7HLjoos5jvJqzhtmnzeBnPlWJDcyzFZ/dg
xs/1sT93SoSIXzMjAqo+TCTZQgr1WjZv8Lo0ewIDAQABAoIBADTV+Nz6gNnREr3S
1vLuedN0PuAGxzyD7MUAeG7c+KEZm287oiN7qD9qw1JmoneBNOLaPRqS6AowjCK5
Om2eUnBRjj04KiKARbSdY8AGSLx7ewiSInjl/NXrv5zr+Ozyjw8Ji/BtPiuCtG+b
gJXj2FDwe+UwXZvH60q1+qK5eP25OYmxTS+KROUDLzKSJwfiyIRwfzTV634KMae7
9x8FTpR4/xnzPh5A9HaixtrZNZye02TvBvTavzRAABF3B7kFOqxhfJn55aJ8zLnF
YZ4SDOuIQtt0hZUgQoZ8on4848H2yjW0FRef2A3VCqTRu3J0AQRJS8JPJ31yX+YK
tyGjYcECgYEA1bFy+uJJ/6g60I9Lu+CQ2Ay/iQo/2TzEYjUa28MPG4KZkkihkfjB
7cgvZwKvWDEUOGAz2GFDwz6H+1oao+hAB+VidOMkytGazQz6/V9cYqKmZk4kJrw7
1EHLgkpFfHeG//WBGwKIINj0RLvfXx8ioq8ktrfAil48ozS3toLUHlsCgYEAoW3d
tANQxTwoAlD5I6rzGBqxwCoA6JegBNsIsob4rB/R3zKJA52utEECI8i449NN6hmQ
84L6JaodXe3XRlIa1saucIe5jezgRca0etzYviuYOQ0PsEqRMKYKeBo72X6LzEa8
GZjV+d4rpvo71mmK892V2OpY1WoEzQ58bmj2XGECgYAQYaoO0YoaryrTEikcHfr8
lP2Z489BOAdV//wvHKTr1vcu36KDLi6vq8j2fJ40hI6oQ7e1vr8TGJgUDLQ+HG/M
KymBDGilo6vaTERxZ/4NEarv7M2YqpVrkB+pvUfWYtNWi9t51pfY7MjM/BoDkL92
+TY3S57W/KJpYIE03JKmQQKBgQCQ/1AuSvQX1SrSucyunvRvaDrUsmXSha7z7ZHo
WZevc31dj9TF7LJpsiKr5bU83iWT6pbqQ3FQt3ZdUi8VONZmqFszNJYUxvnDcvHV
kd0VI689P2AiJzg2jE3HBzlO6H3FZJu8Gi3InCh1eTqaIn7vAM+B4S0dtHbPgP1/
ZsQywQKBgG4XNt+YyqdDvD406sWzQ2m+C+JQMeINn6QdDdW8rg1xLiTFd7vYYPYD
j6ohBSQRgnVmMc0Q4efYP0TI978Mf1f5H/BCU+6azR/L6CapqhrDTtYY13iscyuV
R7AQK4iPNeR6ls92AY2W+PJGIYiByk+7JbOXX/gvPTX7F+/6NsRq
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/${kibana_service_name}.key"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDSjCCAjKgAwIBAgIVANfV55rdCci2edv4n6+zvIQ+TxWoMA0GCSqGSIb3DQEB
CwUAMDQxMjAwBgNVBAMTKUVsYXN0aWMgQ2VydGlmaWNhdGUgVG9vbCBBdXRvZ2Vu
ZXJhdGVkIENBMB4XDTIxMDExMzA4NDA0NloXDTI0MDExMzA4NDA0NlowNDEyMDAG
A1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5lcmF0ZWQgQ0Ew
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCKgXUkoslTKKVeDMsfR9wW
/jcT1ap576/BXrXK4LHgD8Cd2yGoQkS7aswln5KGM2X6k7qRGN6zMJuZq7yN88dP
FVmU8/r8fKfhbhpwpus0Y3NyziSTIcZRoendx3I1jktEDcFFcB1yoVdbClh6S4Z+
MkxHhCwBATvCCmNrwISbLLGyfYkmO10PW8zD/ly1UkSZJ//xfLBtL1u34Q5Aw38r
eBzxBIZRP5hBwnMXUiGo8Kz6ugJ+Qu7YbVL8z1Ie7icIsgjH8mulR23FZjEb5SXm
0sVchA2vDLPkzdJCI8oDgrbT2KBSkr4u+wuo6VDDQsLWaI+uPhULHwdGQUVinliT
AgMBAAGjUzBRMB0GA1UdDgQWBBSZKwtpZ3xXQ2hjW+yj0YRsvLb8NTAfBgNVHSME
GDAWgBSZKwtpZ3xXQ2hjW+yj0YRsvLb8NTAPBgNVHRMBAf8EBTADAQH/MA0GCSqG
SIb3DQEBCwUAA4IBAQBI9jkC3/B2SYc0v/uIS4AZ/7zvLi/bH+D2PsI9+Rhm7ae5
rqXlN2eG8xdTKi4WTKLHOESJWeY5NSK6wAT5CPr1gfByzDAfFbnrwTtz4ELnAiw9
Z4yTU/0ticQ4/d4vJXUPWZ8vqKCi6oTemPhdX0QoO65TKWYZRaaIPgKox+Q4VUP9
LIUT7NBJn+Z5j+Bbyse0dQwzbKhUEOuQOfMcj7pyKFGeqVUEpRdbpEQ70hlHkwZ7
Hon4+ZsQ95BgCpPCm1rHSy/sJgiJ971CmwVJO8TjBgd4iwCit4x+EcFWsVUra/g0
+FKz2L0enirRpzXpG4aNI/bSpiR3yLxAMENFkpo0
-----END CERTIFICATE-----
EOF
        destination  = "secrets/ca.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAioF1JKLJUyilXgzLH0fcFv43E9Wqee+vwV61yuCx4A/Andsh
qEJEu2rMJZ+ShjNl+pO6kRjeszCbmau8jfPHTxVZlPP6/Hyn4W4acKbrNGNzcs4k
kyHGUaHp3cdyNY5LRA3BRXAdcqFXWwpYekuGfjJMR4QsAQE7wgpja8CEmyyxsn2J
JjtdD1vMw/5ctVJEmSf/8XywbS9bt+EOQMN/K3gc8QSGUT+YQcJzF1IhqPCs+roC
fkLu2G1S/M9SHu4nCLIIx/JrpUdtxWYxG+Ul5tLFXIQNrwyz5M3SQiPKA4K209ig
UpK+LvsLqOlQw0LC1miPrj4VCx8HRkFFYp5YkwIDAQABAoIBAQCKDA3dvgI7SD/K
RaYOP2k14Zqzwjpv3l2mtecrllizof+xVj9tnN80jXV76lf4OjJiVeuVwtv0bXYo
6+q68Uato/HtbF+0V+pb3YmszjGPva/LtXruyrMHmgGmcqt6haCu66a+tsgjAHw4
2U7mVXBvR2KPxUS2m6wb8o61TuTcY3ATcYb05DN03nB42P6pDt/GVd1QrbKLylOT
Hopsr1ApgxvhPnxC90hgz4wniDI2RYhUgQbasNeC6CuSgjlQVCTl44JUIy/gQf0A
rLX1lEySapHbLr8oxKpkvmfCh519vc9RnFjBIwzO3SAmNRUduZj+XFYJPgeavOjD
5qYI88oBAoGBAMHjNew5mwqxAIjekKoJadv+Qz/xwwU+KA63GrDHqPfrs/4WJHJ7
O0z5xFE5ANMYtC1EIxDfnZ4i3ZlPN3LpdzwPz6veAjUCHYNcf4USvErvawBluHbj
negkbjm7FyzVsyYNfkRk8pUrV4Pbw/eb2+mMeAOBCnuFBL8wWxYDzuUhAoGBALbg
XGwU/zoYzq/xTkChojSJwKXjJovTFNkRgl6OyxdgjIKKogH1e0xYzGLuIk0olUwI
8xP/77VGqnnE/dFnQ3pX0g7wgDwkXRBONnC0z21cNa5uB5cUKFUi4en61u/eORzF
DZjLf4+QQD0CtU9MRz/okQ82LxzkLSR/D4BLfVMzAoGBAKcocrbku0yuaZ2W9PYE
A6ZNQkGA9/gvLG3zYymCGaUVKysmf+nLYMbul1jHYnSc2cok8m57u/I4cQDaER4b
Nlcr8olkcFavKi60sqRSENAyNfgzuqOVffBEaFuRd1uKKlfmTjQ9K/97TIo8EGoL
j799AYNT32u6tOr4j68dPWTBAoGBAK1iJF4Yvi6fzH5FYzKlzDrRi8P7i9UvqGlx
T1BFQ8oDMNSniZgf3Olymz0El6Ld4ka3iXchxWvx9rkCir7Zj8FTuAWQAZSDyXQn
IzhSRQNjVEXvbeTQKLknHFeRCe1bnHxpW03NSkCbvDvb8HihUkAGSFnKvno+34nl
qZWyfLy/AoGAaonDtHmKHmhNZF35M6LQ81VmWRLw62LeYIdOCE+9PBMQgM8EtJ1Z
5+F32dIDaP8QCkgYV7AyE1sxQvjYISu5OK2EEyl4aLYm9K0P1eeK6HEXz1HYkZpt
NdZ6+3q7IGzxoqkmJmoR0bjrAZXH3mTEIsWZJTIK7qM+TM02GL8CHSg=
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/ca.key"
      }

      # The service stanza instructs Nomad to register a service with Consul.
      #
      # For more information and examples on the "task" stanza, please see
      # the online documentation at:
      #
      #     https://www.nomadproject.io/docs/job-specification/service.html
      #
      service {
        name              = "${kibana_service_name}"
        port              = "http"
        tags              = [ "${kibana_service_name}$${NOMAD_ALLOC_INDEX}" ]
        check {
          name            = "Elastic Kibana Transport Check Live"
          port            = "http"
          type            = "tcp"
          interval        = "5s"
          timeout         = "4s"
        }
        check {
          name            = "Elastic Kibana HTTP Check Live"
          type            = "http"
          port            = "http"
          protocol        = "https"
          method          = "GET"
          tls_skip_verify = true
          path            = "/"
          interval        = "5s"
          timeout         = "4s"
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
        cpu           = ${kibana_cpu}
        memory        = ${kibana_memory}
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
            static    = ${kibana_port}
          }
        }
      }
    }
  }
}
