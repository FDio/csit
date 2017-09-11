# Purpose
This set of ansible playbooks deploy the components necessary to collect and visualize resource usage from servers using:
* collectd
* influxdb
* grafana

It also deploys a log collection and query platform using:
* logstash
* elasticsearch
* kibana

# Playbooks organization
```
├── README.md
└── ansible
    ├── inventory
    │   └── static
    └── playbooks
        ├── collectd.yml
        ├── common.yml
        ├── elasticsearch.yml
        ├── fluentd.yml
        ├── grafana.yml
        ├── group_vars
        │   ├── common
        │   └── grafana
        ├── influxdb.yml
        ├── kibana.yml
        ├── logstash.yml
        ├── mon.yml
        ├── ntp.yml
        ├── roles
        │   ├── collectd
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── collectd.conf.j2
        │   ├── collectd.retry
        │   ├── common
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── hosts.j2
        │   ├── elasticsearch
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── elasticsearch.yml.j2
        │   ├── fluentd
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── td-agent.conf.j2
        │   ├── grafana
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── grafana.ini.j2
        │   ├── influxdb
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── influxdb.conf.j2
        │   ├── kibana
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── kibana.yml.j2
        │   ├── logstash
        │   │   ├── files
        │   │   │   ├── logstash.repo
        │   │   │   ├── logstash.yml
        │   │   │   └── syslog.conf
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   ├── tasks
        │   │   │   └── main.yml
        │   │   └── templates
        │   │       └── openstack.conf.j2
        │   ├── ntp
        │   │   ├── files
        │   │   │   └── ntp.conf
        │   │   ├── handlers
        │   │   │   └── main.yml
        │   │   └── tasks
        │   │       └── main.yml
        │   └── virl
        │       ├── handlers
        │       │   └── main.yml
        │       └── tasks
        │           └── main.yml
        └── virl.yml
```
## roles
The roles are enclosed in the ```ansible/playbooks/roles``` directory. The provided roles are:
* **common**: common applies to every hosts.
* **collectd**: installs and configures collectd to collect metrics and ship them to influxdb
* **elasticsearch**: installs and configures elasticsearch for indexing the platform logs
* **grafana**: installs and configures grafana to query and visualize metrics
* **influxdb**: installs and configures influxdb to store and query collected metrics
* **kibana**: installs and configure kibana to query or browse logs stored and indexed by elasticsearch
* **logstash**: installs and configures logstash to collect logs and ship them to elasticsearch
* **ntp**: *(Optional)* installs ntp to synchronize clocks
* **virl**: *(Optional)* customize virl installation (i.e. openstack services logs and verbosity)

# Usage
the inventory file will be populated with the required targeted hosts information.
Gathering hosts facts is a way to check the hosts connectivity from ansible.
```
$ ansible -i inventory/static -m setup all
```
Should return facts from every host in the inventory

The main playbook for an overall deployment across every hosts is the 'mon' playbook. It can be triggered as follows:
```
$ ansible-playbook -i inventory/static playbooks/mon.yml
```
This playbook will apply the following roles to the targeted servers
* common
* influxdb
* collectd
* grafana
* elasticsearch
* kibana
