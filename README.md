# ansible-weblogic-osb-cluster-installation

The playbooks here will help:

- installing weblogic application server in multiple machines, clustering them and adding to a domain
- installing weblogic application server with Oracle Service Bus (OSB) in multiple machines, clustering them and adding to a domain
- optionally installing ActiveMQ, and configuring JMS and Database resources

It contains the following roles. These roles are very granular for better flexible mix and match

- java - installs java
- activemq - installs activemq
- wls-install - installs only weblogic
- osb-install - installs weblogic and osb
- rcu - Creates database schema required by weblogic and OSB
- wls-admin-server-setup - creates domain, weblogic admin server, weblogic managed server, and adds to the domain
- osb-admin-server-setup - creates domain, weblogic admin server, OSB managed server, and adds to the domain
- remote-server-setup - Creates managed server and adds to domain
- project-config - add JMS and Database resources
- operations - start and stop admin and managed servers

## Tested using:

- CentOS 6.9
- Weblogic 12c
- OSB 12c
- ActiveMQ v5.15
- Python 2.7

## Usage:

- download the _fmw\_12.2.1.2.0\_infrastructure.jar_ and _fmw\_12.2.1.2.0\_osb.jar_, and place them in the _download\_folder_
- download this repository, and go to folder ansible-weblogic-osb-cluster-installation
- update _inventory/prod/osb/hosts_ for host details, and _group\_vars_, _host\_vars_ to customize the hosts, folders, ports etc
- execute _ansible-playbook -i inventory/prod/osb install-multi-machines-multi-servers-osb-cluster.yml_ to install multi-node OSB server
