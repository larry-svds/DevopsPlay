# Ansible Configuration files.

## The Configuration files of Mantl

In order to run ansible you need to have python2 and pip installed and the packages
found in `requirements.txt`

once you have python and pip installed run:

    pip install requirements.txt

with that you have to set up your `security.yml` by running `./secuirty.setup`
and finally you can run

    ansible-playbook -i plugins/inventory/terraform.py -e @security.yml terraform.yml

where `plugins/inventory/terraform.py` could be any ansible inventory file and
`terraform.yml` is the custom Mantl playbook for your cluster.  `terraform.sample.yml`
is an example.

### ansible.cfg

The key things here are
1. `callback_plugins = plugins/callbacks` line identifies where to find the
`CallbackModule` class definition.  #todo where is this used.
2. `hostfile = plugins/inventory` line identifies where to find the ansible host
inventory.  Mantl is set up for a dynamic inventory from a terraform run but
if you have your own set of servers already set up you should be able to set up
your own static file and set your own Inventory.  See *The Inventory* section.


### The Inventory

The inventory is set in the `hostfile=` line in the `asible.cfg`. Mantl.io actually
starts from a terraform run,

Ansible docs.  http://docs.ansible.com/ansible/intro_inventory.html

You can also get dynamic inventory from ec2.  http://docs.ansible.com/ansible/intro_dynamic_inventory.html

An example of the inventory is `vagrant\vagrant-inventory`.  This gets used in `vagrant/provision.sh`.

This should work for my home system.  The default location of a host inventory is `/etc/ansible/hosts` but can be specified on the ansible-playbook command line as option `-i`

    control01 ansible_host=172.16.222.6 ansible_user=centos
    control02 ansible_host=172.16.222.7 ansible_user=centos
    control03 ansible_host=172.16.222.8 ansible_user=centos
    resource01 ansible_host=172.16.222.11 ansible_user=centos
    resource02 ansible_host=172.16.222.12 ansible_user=centos
    resource03 ansible_host=172.16.222.13 ansible_user=centos
    edge01 ansible_host=172.16.222.16 ansible_user=centos
    edge02 ansible_host=172.16.222.17 ansible_user=centos

    [role=control]
    control[01:03]

    [role=worker]  # for some reason the sample ymls use worker here
    resource[01:03]

    [role=edge]
    edge[01:02]

    [dc=kafushery]
    control[01:03]
    resource[01:03]
    edge[01:02]

note that I am defining each host with a name in ansible.  This is not necessarily
a dns name.  This allows me to set up a machine for the playbooks without having
a resolvable name.

### The Mantl Ansible playbook

This is the full `terraform.sample.yml`.  

The first part simply makes sure you run `security-setup` or at least know that
all security will be turned off in all your systems.

    # CHECK SECURITY - when customizing you should leave this in. If you take it out
    # and forget to specify security.yml, security could be turned off on components
    # in your cluster!
    - hosts: localhost
      gather_facts: no
      tasks:
        - name: check for security
          when: security_enabled is not defined or not security_enabled
          fail:
            msg: |
              Security is not enabled. Please run `security-setup` in the root
              directory and re-run this playbook with the `--extra-vars`/`-e` option
              pointing to your `security.yml` (e.g., `-e @security.yml`)

Items to run against all hosts in the system.  The all group in  an inventory does
not need to be specified.  It is set up and contains all the hosts referenced in
the ansible inventory file.

    # BASICS - we need every node in the cluster to have common software running to
    # increase stability and enable service discovery. You can look at the
    # documentation for each of these components in their README file in the
    # `roles/` directory, or by checking the online documentation at
    # microservices-infrastructure.readthedocs.org.
    - hosts: all
      vars:
        # consul_acl_datacenter should be set to the datacenter you want to control
        # Consul ACLs. If you only have one datacenter, set it to that or remove
        # this variable.
        # consul_acl_datacenter: your_primary_datacenter

        # consul_dns_domain is repeated across these plays so that all the
        # components know what information to use for this values to help with
        # service discovery.
        consul_dns_domain: consul
        consul_servers_group: role=control
      roles:
        - common
        - lvm
        - collectd
        - logrotate
        - consul-template
        - docker
        - logstash
        - nginx
        - consul
        - dnsmasq

resource//worker node specific installs.  Basically Mesos in slave mode.

    # ROLES - after provisioning the software that's common to all hosts, we do
    # specialized hosts. This configuration has two major groups: control nodes and
    # worker nodes. We provision the worker nodes first so that we don't create any
    # race conditions. This could happen in the Mesos components - if there are no
    # worker nodes when trying to schedule control software, the deployment process
    # would hang.
    #
    # The worker role itself has a minimal configuration, as it's designed mainly to
    # run software that the Mesos leader shedules. It also forwards traffic to
    # globally known ports configured through Marathon.
    - hosts: role=worker
      # role=worker hosts are a subset of "all". Since we already gathered facts on
      # all servers, we can skip it here to speed up the deployment.
      gather_facts: no
      vars:
        consul_dns_domain: consul
        mesos_mode: follower
      roles:
        - mesos

Control nodes have a lot more coordination software to install.

    # the control nodes are necessarily more complex than the worker nodes, and have
    # ZooKeeper, Mesos, and Marathon leaders. In addition, they control Vault to
    # manage secrets in the cluster. These servers do not run applications by
    # themselves, they only schedule work. That said, there should be at least 3 of
    # them (and always an odd number) so that ZooKeeper can get and keep a quorum.
    - hosts: role=control
      gather_facts: no
      vars:
        consul_dns_domain: consul
        consul_servers_group: role=control
        mesos_leaders_group: role=control
        mesos_mode: leader
        zookeeper_server_group: role=control
      roles:
        - vault
        - zookeeper
        - mesos
        - marathon
        - chronos
        - mantlui

The Edge nodes just run traefik a dynamic reverse proxy application.  

    # The edge role exists solely for routing traffic into the cluster. Firewall
    # settings should be such that web traffic (ports 80 and 443) is exposed to the
    # world.
    - hosts: role=edge
      gather_facts: no
      vars:
        # this is the domain that traefik will match on to do host-based HTTP
        # routing. Set it to a domain you control and add a star domain to route
        # traffic. (EG *.marathon.localhost)
        #
        # For those migrating from haproxy, this variable serves the same purpose
        # and format as `haproxy_domain`.
        traefik_marathon_domain: marathon.localhost
      roles:
        - traefik

GlusterFS is a unique problem.  You want to provide shared distributed storage to
all the worker nodes.  Here the control nodes are feeding gluster to the workers.
On the mantl gitter there is plenty of discussion of problems with this.

Additionally you ahve to set up bricks and in a physical cluster This facility is probably best set up manually.


    # GlusterFS has to be provisioned in reverse order from Mesos: servers then
    # clients.
    - hosts: role=control
      gather_facts: no
      vars:
        consul_dns_domain: consul
        glusterfs_mode: server
      roles:
        - glusterfs

    - hosts: role=worker
      vars:
        consul_dns_domain: consul
        glusterfs_mode: client
      roles:
        - glusterfs
