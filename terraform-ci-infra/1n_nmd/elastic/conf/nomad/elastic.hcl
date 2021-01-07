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
          "secrets/instances.yml:/usr/share/elasticsearch/config/instances.yaml",
          "secrets/users_roles:/usr/share/elasticsearch/config/users_roles",
          "secrets/users:/usr/share/elasticsearch/config/users"
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
instances:
  - name: 'elastic0'
    dns: [ 'elastic0.elastic.service.consul', 'elastic.service.consul']
  - name: 'kibana'
    dns: [ 'kibana.service.consul' ]
EOF
        destination  = "secrets/instances.yml"
      }
      template {
        data         = <<EOF
elasticuser:$2a$10$kgJDjo1/pBaBsnUHvsGOiOT3IAJhk2TBVNJeTv/1EPg//klcJCK4y
EOF
        destination  = "secrets/users"
      }
      template {
        data         = <<EOF
kibana_admin:elasticuser
monitoring_user:elasticuser
superuser:elasticuser
EOF
        destination  = "secrets/users_roles"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDaDCCAlCgAwIBAgIUG3esFYSWamMDpavP3zw/JTA5svswDQYJKoZIhvcNAQEL
BQAwNDEyMDAGA1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5l
cmF0ZWQgQ0EwHhcNMjEwMTE0MTQwODU2WhcNMjQwMTE0MTQwODU2WjATMREwDwYD
VQQDEwhlbGFzdGljMDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALUU
ZYRGTcGz4NrP7vIzZo5kDBekffRYugqBzfDztNtfqBPEKB/rK9tJr8Qp2IfKJJ0l
yuMTkYUcebjKIHfOJ4MAvNKtA1lSj3j0FJSOw9LXFuIYKCD661RmdWiwnz4pAVIs
oAriQmz/Z1hib38vmZ7dyYgS1VkUssHDxKM9q/9Q1ILmuOtuOJN6e5shnGNTm2Ft
j3uNk8ZTHBOM4LiCBu4tQ3v1DIjdT4t2pG5grQu374Sinux3YlcIeuxQbpAVaOl+
gfQnK7skdtXWMYVmZnuMJpRRIxzWyhsAlWaOletbjQ3xOqW/oXtfg9ve6qPhFJuC
s5l3YqufKlXVoyrbXCkCAwEAAaOBkjCBjzAdBgNVHQ4EFgQUKLG4/6t+9LtjH18Q
7PTFas+YXzAwHwYDVR0jBBgwFoAUYgsxZu+uL3YBbh6EoB7W49VgmCUwQgYDVR0R
BDswOYIfZWxhc3RpYzAuZWxhc3RpYy5zZXJ2aWNlLmNvbnN1bIIWZWxhc3RpYy5z
ZXJ2aWNlLmNvbnN1bDAJBgNVHRMEAjAAMA0GCSqGSIb3DQEBCwUAA4IBAQAEepAs
h7d+a2k6Qj7B3KyZnX0O50toeZW+tKnnfGin0H5LGgvVn40mRJEJKBzatp/LvHh+
x//YM+x8IbZe7bDtf69EUqq6C3881Xsq1jj77GZ1buEP+W9nRNjM3o4mjcn3RfPw
GRV6lHnpHvhqAUIFtlOHvaa0UuEbqQkomxr/e44btRdnDQ6SRRh4xwBKYT/O/a7O
YpS514Q4vKNQ6XLSAdGpJjK6KdHO5xkzCi4zYastpuy8ct/qqiAklAtXaF+7F0OX
riSs0AsAokMsF+hLv5d1kAH535uHs7Mr85gw7Y7/qlXmJovh4oWcys8XTPvlHhkQ
98I9yFJ7HRAUgbah
-----END CERTIFICATE-----
EOF
        destination  = "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAtRRlhEZNwbPg2s/u8jNmjmQMF6R99Fi6CoHN8PO021+oE8Qo
H+sr20mvxCnYh8oknSXK4xORhRx5uMogd84ngwC80q0DWVKPePQUlI7D0tcW4hgo
IPrrVGZ1aLCfPikBUiygCuJCbP9nWGJvfy+Znt3JiBLVWRSywcPEoz2r/1DUgua4
6244k3p7myGcY1ObYW2Pe42TxlMcE4zguIIG7i1De/UMiN1Pi3akbmCtC7fvhKKe
7HdiVwh67FBukBVo6X6B9CcruyR21dYxhWZme4wmlFEjHNbKGwCVZo6V61uNDfE6
pb+he1+D297qo+EUm4KzmXdiq58qVdWjKttcKQIDAQABAoIBAQCMeL4n1sILOhd8
p0Gd8fHlFAetb5WmMA5iiD/SY7wxUgt5Cfp2iGEFRCxt6GhpLo8ouWCit1N0B5sF
lweI6QwNvEy+wiiO6lUSZ4ZvmDChJupBiqvWqdBVMQZzqFBgUD8OGEAvMUaGd7sb
/YCxEaQCcdsdDD8lU8E4Pz4TxIvhCukcFV/Jd60yh2K7UAnruG8ZcytmTsfnA7s7
IIsnu20YllwflSjkb3oKtOsgKjMc6Oj01vjH90W+UXC7S+OJ/bXdCCBJn6QYfVRd
IQ9l0bvtu+4yoRBmXRbIJ6zf8++FOBXa25I5U2VJbw44VszlZfeRahqoxF8jrSTh
7uZZr3HhAoGBAPwM30AmGP0msTbJSm5KhSdwhxLtQ1xAd3z8HmgEQ99ncdeVqJ/b
kHh6L3UW+0kLHHvJs0D4xlr6CJrZBRtwJLxuE7dtlBD7ouvVZjdQ09drKio7/aC3
L3/spyRAw7yHlZFVkvNapZV9TUfcpwrza4FUiHdhATw7YhPQQ53x54t3AoGBALfq
0WRksjZrMSxQWzPCBkVx1efc6WzednV8FJFldLbA1+sVi1g0fSW6y5EK/gHgezIp
EdyG937lUnXyCYxMH+LuZUkq2ZyUjpH/pQxCBXpmwDA8shRD/UTBtpd/x/ORapCs
PF/sC5eXATyQX7ADWQeeTZndWICNQuLNf0mKNv1fAoGBAOd8cvWZh83IYW2txTwy
GMS2JngNjJYHZzZU3yAs+qENgpK7Eplur+rWXQuuxa66E7jk8Eq1sIcRqCF/O5+N
iU+90UHf0+MdGO57mVsoUsc/1wPfAPtAAtH8aS10hdB6vbUy4Lm8AOOgpv9e+dOm
6I9pMcRiRR4qc9M6rT88UqnVAoGAblX0eusiMx2JqZEntdxf0MejUW+ppkOsA32G
BVg9deopXwJUz3zl23295G0Yx915azVSXt+lmT5QgyvKaJ2+v3DP2N5ZIOPKyHH6
/WiaSr1b7VRsbVYAmoAwX6EsPsZtjQ+XROCib7YK6t+eWEUZ40UoPveYwb59cv1f
sKm3pbcCgYEAgyYc6DdrsAgT4S9g38hdqtuiSejhcGojHVeaMmPNxgoaXZZ66+g6
KujDXHJtkUCBluXOhfsQcjAr2UzvxpGdvDd5Ym5HA6l/2qAtph+f8DUofESSz7vh
T9/4PLw82sIU9/wFM40F1IV20W1TgUnJZln4HdpWPpwmXottoOX3y2s=
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/${cluster_service_name}$${NOMAD_ALLOC_INDEX}.key"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDSTCCAjGgAwIBAgIUal1tFY90NA8IgvMVUs/jfyG3N00wDQYJKoZIhvcNAQEL
BQAwNDEyMDAGA1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5l
cmF0ZWQgQ0EwHhcNMjEwMTE0MTQwODU2WhcNMjQwMTE0MTQwODU2WjA0MTIwMAYD
VQQDEylFbGFzdGljIENlcnRpZmljYXRlIFRvb2wgQXV0b2dlbmVyYXRlZCBDQTCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKBXjJFIv4LL2DfqhUdPQGJl
MmTgxIvqkDsoOxDYuTP27hY27wKUWFBO0sYkWxpddenGQxk66SzkU1XukvGw/Ygs
ezyuvRZq2UlOOt+2eIIjYmb6TIfhpDbMeVhYXfKiFtRHUYskd2VfSUktff8NEnC1
iWLPQaMdv81CmMOGkshjVYn4gaHD+b8Kv7sfnFn5WYMojWez1OOfWke+lJfw+sIa
tOaZ+ufGZB50H63OZrUJJJa0QahlTakHJpXrk5x0mUq/E9P74FUFQ+tDqUPjLXQq
aPFbzwtSyiT0Rk8nMqu2TQm0kkz79wjR44MmXJo+qFAbMVY/fam+kLEpth0UL9UC
AwEAAaNTMFEwHQYDVR0OBBYEFGILMWbvri92AW4ehKAe1uPVYJglMB8GA1UdIwQY
MBaAFGILMWbvri92AW4ehKAe1uPVYJglMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZI
hvcNAQELBQADggEBAG4SEZ6beme+BG00ybv4YcFVEhUI24jgrpntyIOHC2ARkLXW
1yl22Ue/eRg8fP9UhHH2YmUXt2Fy8b1HzihH38WAO/Wxx2K6u38C2ADuTppELWIU
XUktUCOeYB2B5jbwFSExm6N2Rhj9YJsdlm/Lvph9s2VQThdKUZPOXqdi8u5C6L0k
s2gkrKJdm4hF7NnVcgIzBPBY86sYzOMW1CXFP6o887KxKjPI7A1JAAkrPZz3ob0n
B9pBayly5UAtixLJhQbkDfGAB1gRnDWaCDYmN+YT4LaQ/tsqueW8Ba1hQ1PqVLvw
6J6ytch0M9sCIQe1PzLhEJRpfqtqeacr8yEUgkg=
-----END CERTIFICATE-----
EOF
        destination  = "secrets/ca.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAoFeMkUi/gsvYN+qFR09AYmUyZODEi+qQOyg7ENi5M/buFjbv
ApRYUE7SxiRbGl116cZDGTrpLORTVe6S8bD9iCx7PK69FmrZSU4637Z4giNiZvpM
h+GkNsx5WFhd8qIW1EdRiyR3ZV9JSS19/w0ScLWJYs9Box2/zUKYw4aSyGNVifiB
ocP5vwq/ux+cWflZgyiNZ7PU459aR76Ul/D6whq05pn658ZkHnQfrc5mtQkklrRB
qGVNqQcmleuTnHSZSr8T0/vgVQVD60OpQ+MtdCpo8VvPC1LKJPRGTycyq7ZNCbSS
TPv3CNHjgyZcmj6oUBsxVj99qb6QsSm2HRQv1QIDAQABAoIBADz9EBqy8SVvI+8g
5VEadAL5OxHj7N7LedEGnHDr/oYlhqosev0gL/dcBBAaBA0jP5aMMzmFjuvkbU5i
UMJd8BG72aRbUtEUE1Iuz3YIkg3uJ5/D1RhaW3v8iqtv8Uw5GzXjasDiPgfxFo8f
Hq3E6x6z7m4HJ5BD4JDSpAi7R1mw0VmklleDG/7FjCbWjyJIbv9I0337uqiFQJ6t
ERPf7+LK0mdaBvhPcWBSShXPi0p6kTe+/DcWmcf9ORBII9PRipd0bViSoot4xSWc
6DKjY0lDK23C4YPNOFb5aI4BfsMxcXhEnf6oAx1+oKDgGSDrPmMtuUB3OzdWPeBv
ZUtAZAECgYEA+pHYIX+KQ+cDBgFxlzZwQBUVRZzie9twUCZrAXcrV4qTSbI3ML1f
TrzSzDsdfVYuPUUCy5hbSJ5SqYchZ09oWhKXgfffsHwgMO2faN7iUYPvFKyxUrMS
+Gj8VgkiQEV3ka820LxDbaVc34R6kkoOnRt1QSohoARZzmN/0K9/pe0CgYEAo9Ef
jdpS0HF7nlJ2lc7WJirKdg8ECCVuswD7Ay4SKz1/pIcSdTES2w1204d1v14jPt/S
coy5VT28CT4Zfn/D9yhj/NvIG9IKshAGClcVAkH+Uh9iXBIZvPzashZD6Xp0FfRj
5QX6koiS8Jxnf2A+1s5SLNKPnWoPwWnKCvJJdIkCgYEA0x/X8EG6ioQ3c/P7deGU
qyoYhlMuMhYviBkWyGFUz6ofeFUFU7f8eid3pkWZD2ZyB4YCWPHC2GkuVVFav+WU
k3Be4E+u1tF/fjp5uq8yGmUEKXNo5bmlHlG3a/a+OVFO8h2kHjTCy7wtiNfjPyfP
MGlWXtXVBzMjSFdl9rwo3fECgYA1tOPxb7hi2jG7EDIMn0kaLkE+P2IFAbCvQw0I
V9xhDMKCQD5O6Y3S/zEL3Ic//C71+A9YusYwKhMxvIhDLsQijb1qMuwCIvSauCIi
1bXvjY9BgUSQBuclTIiuhhoxu5G/eOYfObySue/iroRIAFfZuL68LzQiWZlcwcAZ
oqFucQKBgCFUFgFc9LebqwBC/3nEgeAkDRutipp8TQOw4ZFCVI43ShFNz4CJqaq9
uFBgoI6tMoc5LDBTzs7rJvijcWN44pbo2COVPHQZDCNsI15G0t5JjY0cOz426D9r
RVhLPYqpE6zQHy35PAnZnYQ8h/VfIsmGvkczjeADPIXR8jyf6FQ7
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
          header {
            Authorization = ["Basic ZWxhc3RpY3VzZXI6RWxhc3RpYzEyMzQ="]
          }
          tls_skip_verify = true
          path            = "/_cat/health?pretty"
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
    task "prod-task1-elastic-kibana" {
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
          "--elasticsearch.hosts=https://${cluster_service_name}0.elastic.service.consul:9200",
          "--elasticsearch.username=elasticuser",
          "--elasticsearch.password=${cluster_password}",
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
          "secrets/ca.crt:/etc/kibana/config/certs/ca.crt"
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
MIIDQzCCAiugAwIBAgIVAOckTq6CgphZAuFRgi8dAgkk3mIIMA0GCSqGSIb3DQEB
CwUAMDQxMjAwBgNVBAMTKUVsYXN0aWMgQ2VydGlmaWNhdGUgVG9vbCBBdXRvZ2Vu
ZXJhdGVkIENBMB4XDTIxMDExNDE0MDg1N1oXDTI0MDExNDE0MDg1N1owETEPMA0G
A1UEAxMGa2liYW5hMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsAbC
Te1t0tZFDO9stsqpl1g16DPGuk4hqe5HrXBDRk1atswitJ5+hVdWnCiZ9zBHsXLO
DN5m9AkqYe4r9e7+CIAW6v3TzvYa6qP9rQVt873l/zJnZp1mS2Cro+HdLctXCTW3
3OC7VjIOmGidbNFPWe+Nh5Plp2u9eQSDLJ3OGx0Q9GlQAUp9dbHsauWpLBy0YRsQ
X+0UHTm9Nx04cNZGilC12F/LuJtuqFiqCSQ/QAPmb+AJWsTZAPlhQl7raNh6Ghcj
O11GZzlQQ1MWjNCaBtsRFJsOrbYbK5qbvZUbm9FPDjlKCZ7TCrVcjwwYrP/9HvfV
CS9eQ+Q7JhxjKV6zowIDAQABo28wbTAdBgNVHQ4EFgQU39rJmu9XDHTDDyvKAIPr
P6Fek5MwHwYDVR0jBBgwFoAUYgsxZu+uL3YBbh6EoB7W49VgmCUwIAYDVR0RBBkw
F4IVa2liYW5hLnNlcnZpY2UuY29uc3VsMAkGA1UdEwQCMAAwDQYJKoZIhvcNAQEL
BQADggEBAD8ySxda8bqehs4ZdmdFBe0n0Fqo6KK8rRCGqKu/qpzuSA9/T372NE/k
Whx3QQPWcb3DhS+oEZ2s8KPrq6pSZtDcQqMWusxeNX7L/V0FLtKneksP8w/y0Wb4
KeAss66DVrr6Jl1WNzPO0Ia9SugQa4gcXf6M6sH72NqgQZMqfkUoPw3OrKxgD7zD
ww/eKW82CRW1/SkHEbpgIhT4zl2MOnlIT1XGBl+OdFLlTo9QQJtZl4+p9VBvvuVC
KwdU1h+0YRL7ktT3JcmVdvloxmQljymCx4AttPAZubXDVr0r02ne51bJw92gomHY
oG/i7diepgsKwG0txI8FIaF17URHdg0=
-----END CERTIFICATE-----
EOF
        destination  = "secrets/${kibana_service_name}.crt"
      }
      template {
        data         = <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAsAbCTe1t0tZFDO9stsqpl1g16DPGuk4hqe5HrXBDRk1atswi
tJ5+hVdWnCiZ9zBHsXLODN5m9AkqYe4r9e7+CIAW6v3TzvYa6qP9rQVt873l/zJn
Zp1mS2Cro+HdLctXCTW33OC7VjIOmGidbNFPWe+Nh5Plp2u9eQSDLJ3OGx0Q9GlQ
AUp9dbHsauWpLBy0YRsQX+0UHTm9Nx04cNZGilC12F/LuJtuqFiqCSQ/QAPmb+AJ
WsTZAPlhQl7raNh6GhcjO11GZzlQQ1MWjNCaBtsRFJsOrbYbK5qbvZUbm9FPDjlK
CZ7TCrVcjwwYrP/9HvfVCS9eQ+Q7JhxjKV6zowIDAQABAoIBAQCQJQjKTaqIY6Rp
4kpRKYZVBAwo2PVcrQyOHi0eDvdYQ5IMbP/ijoOm541qFSl3rVaYLh4jlaATKMpH
JYVkQFBQX6vkxPTE3u3NxXq/S9ntJk2IfBsGgdA527DSY+v+Syw7w3yL6JAgFp+z
GMAJUyG60RtBsc/3GJgw2IweZh9YPUdmgPy6Ci2MutXVJwiRlies9xSDJwgzQHCr
CrJJmhc2kTxX16yBJ/KM1aJjME+/fVBvvr9+QHrK4sqqgMXCtzLCfBRocWcv71kq
tnTVBrYrPH/Wwq//5B5qlshJ99d1V+k4btVpLDqL17iB2bWRYZ00QTluepf0C77n
is/j/uR5AoGBAPJE8zOYePYb6pMnVdMjAtEeR7zPMyr+fqpkTtzaSydLor58cB8z
hyLzW2AeD+2qGAIoojjfnkhZm56/kYMnyuS6+qW2wO6527ts5K37XEMHsPs+33fJ
WN0sOYZM+kBw/3YFsq4o/rl0poj7WObe47GEQqp8cV+r5RgPMDy9AoBvAoGBALoA
szcwYODvR0H8UMCIk0l3QWVAgP8HLDP0ZVJ2GYzek+0nx30LFJLkoMohoxg01FKd
0t3HvsQnyR582hXGmTt5g87BjOTKiFJO1ivMgaNaVoYSF4G4Jiobf5R3Lq0tY5od
APu1uW0RfnX1vDaCEFaphFhb57n+7us0rhfSn7INAoGAT3a+LpY8Vr0hW9LzG6XI
Lr832H490kRXV5w/IcGYFPOCFejK/fDwyk34ErbJkrLP3SVm0DDIwgJiQNek6tgK
fKu3utMOxT7BC+DTwR1JTdMgAcjFk4y/UQxIcfyduLVXlWaZDPb1Ve8lEJkgt9kz
5e3zz+exaCgBpLqWn9V/FJECgYBFlpN2N2RXY04Okt6HWdF47+QIhJx+TWmtOmdZ
9ZNTj8ZaOMK6tpWI6354gSMqoEE7c457qQpnCteEz4MsGHQluy2kAee7hUaBPLuG
AWoS+m5alJQ01Pd6U3Vkzz4oTk3wT5+ZjICGHMBqU3iKEBkawysff6rvfEBYwQnN
IeDbVQKBgFIz6Inou83siOUhFbDZnLmedRGINPw5NJiHpRS/x8rdWAN1brrvqj+l
FKwTUHgHnazREeLFlQ4kRvdKK+zogJPfA9T0Zetf49YHYuG08+oo4pZSrtbabacZ
nES7vAtMC5TCvwKTNXBk1nbxdX3jVFJl88wiTpBbnwSqnjt/Ta8t
-----END RSA PRIVATE KEY-----
EOF
        destination  = "secrets/${kibana_service_name}.key"
      }
      template {
        data         = <<EOF
-----BEGIN CERTIFICATE-----
MIIDSTCCAjGgAwIBAgIUal1tFY90NA8IgvMVUs/jfyG3N00wDQYJKoZIhvcNAQEL
BQAwNDEyMDAGA1UEAxMpRWxhc3RpYyBDZXJ0aWZpY2F0ZSBUb29sIEF1dG9nZW5l
cmF0ZWQgQ0EwHhcNMjEwMTE0MTQwODU2WhcNMjQwMTE0MTQwODU2WjA0MTIwMAYD
VQQDEylFbGFzdGljIENlcnRpZmljYXRlIFRvb2wgQXV0b2dlbmVyYXRlZCBDQTCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKBXjJFIv4LL2DfqhUdPQGJl
MmTgxIvqkDsoOxDYuTP27hY27wKUWFBO0sYkWxpddenGQxk66SzkU1XukvGw/Ygs
ezyuvRZq2UlOOt+2eIIjYmb6TIfhpDbMeVhYXfKiFtRHUYskd2VfSUktff8NEnC1
iWLPQaMdv81CmMOGkshjVYn4gaHD+b8Kv7sfnFn5WYMojWez1OOfWke+lJfw+sIa
tOaZ+ufGZB50H63OZrUJJJa0QahlTakHJpXrk5x0mUq/E9P74FUFQ+tDqUPjLXQq
aPFbzwtSyiT0Rk8nMqu2TQm0kkz79wjR44MmXJo+qFAbMVY/fam+kLEpth0UL9UC
AwEAAaNTMFEwHQYDVR0OBBYEFGILMWbvri92AW4ehKAe1uPVYJglMB8GA1UdIwQY
MBaAFGILMWbvri92AW4ehKAe1uPVYJglMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZI
hvcNAQELBQADggEBAG4SEZ6beme+BG00ybv4YcFVEhUI24jgrpntyIOHC2ARkLXW
1yl22Ue/eRg8fP9UhHH2YmUXt2Fy8b1HzihH38WAO/Wxx2K6u38C2ADuTppELWIU
XUktUCOeYB2B5jbwFSExm6N2Rhj9YJsdlm/Lvph9s2VQThdKUZPOXqdi8u5C6L0k
s2gkrKJdm4hF7NnVcgIzBPBY86sYzOMW1CXFP6o887KxKjPI7A1JAAkrPZz3ob0n
B9pBayly5UAtixLJhQbkDfGAB1gRnDWaCDYmN+YT4LaQ/tsqueW8Ba1hQ1PqVLvw
6J6ytch0M9sCIQe1PzLhEJRpfqtqeacr8yEUgkg=
-----END CERTIFICATE-----
EOF
        destination  = "secrets/ca.crt"
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
