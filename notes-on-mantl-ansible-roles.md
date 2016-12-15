# Notes on Mantl Roles

###### tl;dr - give mantl a base centos 7 all updated with a seperate volume for lvm configuration and figure out the gluster stuff seperate.  It will need 2 additional partitions on 3 machines for the bricks.

There is a role per technology. Each of these technologies is assigned to different
groups of nodes.  Mantl has 3 node groups; control, resource/worker, and edge.

Check out the discussion of the inventory and the Inventory and the Mantl Ansible
Playbook in [notes-on-mantl-ansible-configuration.md](notes-on-mantl-ansible-configuration.md)

Each of the roles is divided into directories that mean something to ansible.  
There is a good reference in [the Ansible Best Practices page](http://docs.ansible.com/ansible/playbooks_best_practices.html)

* defaults -- main.yml -- seems to be variables
* files -- various -- place to put files that are referenced in tasks and handlers
* handlers -- main.yml -- tasks do things in order and might cause events.. Events that
are handled via a handler.  for example, you might have a task that changes some config
and then that requires several other software systems to need to be reloaded.
This is done with a `notify:` element in the task.  It references the `name:`
in the handler file.  
* meta -- main.yml -- dependencies. For example, the glusterfs role has a dependency on
lvm
* tasks -- main.yml -- The sequential tasks to perform in a playbook.
* templates -- various -- special files that use jinja2 template language to
dynamically create files that are referenced in a task or handler as a template.
* vars -- main.yml -- variables associated with this role.



## Software loaded on all machines

Mantl starts with the current Centos 7 and then adds the following roles.

### Common

 * Set time to UTC
 * add hosts to host file
    * this uses a template to go through all hosts and add its name and IP to
    host file
    * I wonder how ip hosts with ansible names will do #todo: try it
 * install system utilities
 * firewalld disable
 * enable EPEL
 * install pip, update pip, setuptools
 * install distributive
 * users
    * sudoers to no password sudoers
    * add sudoer accounts                             #todo: ??
    * set up ssh keys for the users
    * some strange thing with deleting os users?      #todo: ??

### lvm

Creates a volume group for Docker.

glusterfs has a meta dependency on lvm but I don't see it using it and the
glusterfs docs suggest you dont use it.  #todo: ask in channel about the dewpendency

This is created if `lvm_physical_device` is defined.

For openstack this is `/dev/vdb` for AWS it is `/dedv/xvdh`.  

On a physical stack each machine would need to have a special device for this
purpose.  

it creates a default volume group named 'mantl'  this can be set with variable `lvm_volume_group_name`

This volume gets formatted.  It is default 100 GB on AWS and Google.  


### collectd

This seems to be pegging the vagrant version with a 1 core working 100% forever with no real load.     

I'd like to not include this but there is a collectd configuration in docker role.

This collects system and apparently container statistics and sends it to:
  * collectd compatible reciever at host and port.  Defaults to localhost and 25826
  * syslog at a given loglevel.  Default is only 'err'

### logrotate

This is cool and simple.  Sets up logrotate for mesos, zookeeper, and docker

### consul-template

https://github.com/hashicorp/consul-template

This is used to move values between consul and .. well used to be haproxy.  Not
sure how it is being used now.  #todo: what uses consul-template in 0.5?

Installs and configures for consul.  It is a service.

An interesting thing in this role is that it has a dependency on `role handlers`
basically as things happen they notify handlers which  reloads `systemd, consul and consul-template`.  There is one step that waits for consul to be live before
reloading `consul-template`.  

### docker

The docker role has a dependency on lvm and so this is a bit convoluted. There is
is a boolean `docker_lvm_backed_devicemapper` and lvm code for:

  * This installs `cloud-utils-growpart`
  * installs docker-storage-setup file in /etc/sysconfig

This is all about setting up the storage configuration on centos. Some resources.
  * http://www.projectatomic.io/blog/2015/06/notes-on-fedora-centos-and-docker-storage-drivers/
  * http://northernmost.org/blog/lvm-thinpool-for-docker-storage-on-fedora-22/index.html

Some other features:

  * Installed with selinux turned on.  Hard core.
  * ties docker into syslogd
  * configures docker for consul dns
  * configures private registries `when: do_private_docker_registry`
  * sets up collectd for docker
    * this is pretty involved `roles/docker/tasks/collectd`
    * if I am not doing role: collectd then I need to take out the
    include of this file.

### logstash

Looks like logstash collects off of rsyslog

There is some connection to `distributive`     #todo: figure this out.

Its set up to go to
  * stdout
  * elastic search
  * kafka             #todo: where are these typically located.

### nginx


>`Nginx <http://nginx.org/>`_ is a web and proxy server.
>Mantl uses it in front of the :doc:`mesos`,
>:doc:`marathon`, and :doc:`consul` web UIs to provide basic authentication and
> SSL. Those proxies are set up in the individual roles linked above, and the base
> ``nginx`` role is just used to move the relevant certificates into place.

from roles/nginx/README.rst

Creates the ssl directory and places the certs the directory.   Sets the admin
password.

It also includes some `distributive` configuration.  Distributive works with
consul to provide health checks.  https://github.com/CiscoCloud/distributive

### consul

>`Consul <https://www.consul.io/>`_ is used in the project to coordinate service
>discovery, specifically using the inbuilt DNS server.

from `roles/consul/README.rst`

dnsmasq is serving the /etc/hosts file as DNS on port 53 and passing all consul
domain requests to consul.  

The consul role has quite a few variables you can mess with.

##### Key Variables

  * consul domains

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
  *  consul_advertise -- ip address for Consul
  * a few others

Security:
  * encrypt gossip communication with `consul_gossip_key`
>  If set, this is used to encrypt gossip communication between nodes. This is
>  unset by default, but you *really should* set one up. You can get a suitable
>  key (16 bytes of random data encoded in base64) by running ``openssl rand 16
>  | base64``.
  * TLS `consul_enable_tls` and friends enables TLS authentication.  Default `false`

##### consul tasks

  * install consul, consul-ui, and consul-utils
  * installs the consul config from the following template `roles/consul/templates/consul.json.j2`
  * registers docker
  * deloy TLS
  * configure acl on servers
  * install 'wait for leader' and 'rolling restart' scripts
  * emable and start consul and wait for leader election
  * setup acl agent and restart consul
  * setup nginx as a proxy for consul-ui     
  * register the distributive tests with consul.


### dnsmasq

man page http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html


>The project uses `dnsmasq <http://www.thekelleys.org.uk/dnsmasq/doc.html>`_ to
>configure each host to use :doc:`consul` for DNS.
>
>**Variables**
>
>The dnsmasq role uses ``consul_dns_domain``, ``consul_servers_group``, and
>``consul_dc_group`` defined in :doc:`consul`.

The tasks do the following:
  * install latest packages for dnsmasq, bind-utlis and NetworkManager
  * gather the information from /etc/resolve to rebuild it with the additional
  first namesever of 127.0.0.1 so that dnsmasq is used for dns resolution.
  * configure dnsmasq to send domain consul queries to consul.
  * It can also enable kubernetes `when: cluster_name is defined`
  * sets up distributive tests.  See https://github.com/CiscoCloud/distributive


  ## Software Loaded on Resource/Worker Machines
