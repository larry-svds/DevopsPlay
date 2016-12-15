
## centos install

Don't let the install take the whole drive

Chose to partition manually but then on the manual partition
page you have the option to automatically configure. Choose that and then
modify the /home partition where it puts the rest of your drive.  Fact is
almost nothing actually belongs in home on a microservice-infrastructure  but
its handy to leave some there.   you will want a good 50 to 100 Gigs left
over for an LVM partion for Docker.  

## passwordless login
## host file



## Setting up your lvm

    parted /dev/sda print
    fdisk
    n
    default
    default
    +100G
    w
    reboot


don't put a file system on the partion

## setting up inventory

Setting `lvm_physical_device` to `"/dev/sda4"` or `""`

(actually did this in the bare-metal.yml)

## code changes for provider=physical

in `physical.yml` I added the provider variable.

    - hosts: all
      vars:
        provider: physical

I noticed this was in the vagrant.yml but it was not in the terraform.samle.yml.  The provider must get set in the dynamic inventory.

In Consul configure there is also a error if consul_dc_group is not set.  

in consul's readme.rst you have:

.. data:: consul_dc_group

     The group to look in for the local datacenter. Using the Terraform plugins,
     this should be ``dc=dcname``, and it will default to that with the current
     datacenter name.


In the `vagrant/vagrant-inventory` you have:

    default ansible_connection=local

    [role=worker]
    default

    [role=control]
    default

    [dc=vagrant]
    default


default is a host.  and it looks like they add a dc with all the hosts.

I went ahead and added

    consul_dc_group: all

    (Actually addded dc=dc1 section to inventory)

to vars

if I add a physical provider I need to worry about what happens
in each of the following projects.



#### Calico

provider!=openstack in roles/calico/tasks/calico-configure.yml

#### Glusterfs

The brick device is set based on provider.  

#### Docker

in `roles/docker/defaults/main.yml` :

    docker_lvm_backed_devicemapper: "{% if provider in ['gce', 'openstack', 'aws'] %} true {% else %} false {% endif %}"

    ## Refer to commentaries in ../templates/docker-storage-setup.conf.j2
    ## or `man lvcreate` for acceptable sizes, and their syntax
    docker_lvm_data_volume_size: 40%FREE
    docker_lvm_data_volume_size_min: 2G

I added 'physical' to the list making it:  (actually bare-metal)

    docker_lvm_backed_devicemapper: "{% if provider in ['gce', 'openstack', 'aws','physical'] %} true {% else %} false {% endif %}"

in `roles/docker/tasks/lvm.yml`

    # dependency for cloud-utils-growpart
    # which is required if we have GROWPART=yes (default) in /etc/sysconfig/docker-storage-setup
    - name: install cloud-utils-growpart package
      sudo: yes
      yum:
        name: "cloud-utils-growpart"
        state: present
      tags:
        - docker
        - bootstrap

This package does not exist for physical.  GROWPART defaults to no.  So the comment here is a bit old or in error.

adding the line:

      when: provider!='physical' (actually bare-metal)

### Seeing That It Worked.

Go to the machine and do `docker info`:

    Storage Driver: devicemapper
     Pool Name: mantl-docker--pool
     Pool Blocksize: 524.3 kB
     Backing Filesystem: xfs
     Data file:
     Metadata file:
     Data Space Used: 1.596 GB
     Data Space Total: 42.9 GB
     Data Space Available: 41.31 GB

Nice article

http://www.projectatomic.io/blog/2015/06/notes-on-fedora-centos-and-docker-storage-drivers/



## Running Ansible Playbook

    ansible-playbook -u lmurdock -K -i physical/inventory -e @security.yml physical.yml -v >& physical.log

    ansible-playbook -u lmurdock -K -i bare-metal/inventory -e @security.yml bare-metal/bare-metal.yml -v >& bare-metal/bare-metal.log

in another window doing:

    tail -f bare-metal/bare-metal.log

## Consul is a pain.

Consul wait for leader can get fail.   Basically if you stop all the servers gracefully you get a cluster than can't come back up.

https://github.com/hashicorp/consul/issues/750

https://www.consul.io/docs/guides/outage.html

All machines are set as server..

So the basics are..

    sudo su
    systemctl stop consul
    cd /var/lib/consul/raft

The file `peers.json` probably has the value `null` if `journalctl -b` is telling you that consul can't find a leader.

edit that file and reenter the hosts in the consul server set.

    [
      "172.16.222.6:8300",
      "172.16.222.7:8300",
      "172.16.222.8:8300"
    ]

Once consul is up.

     systectl status consul

Check consul monitoring in a browser:

    172.16.222.6:8500


## Consul user needs a shell for Distributive

Distributive tests fail with

    This account is currently not available.

When you start.  This is because they run as consul.  

a consul user is created but it is created without a shell.

So

    consul:x:997:995:consul.io user:/var/lib/consul:/sbin/nologin

needs to be:

    consul:x:997:995:consul.io user:/var/lib/consul:/bin/bash



## Mesos Zookeeper

    TASK: [mesos | wait for zookeeper service to be registered] *******************
    failed: [control02] => {"elapsed": 300, "failed": true}
    msg: Timeout when waiting for zookeeper.service.consul:2181

is fixed as soon as consul user has a shell.  Consul is not routing to
zookeeper.service.consul because the health checks are not right.


## traefik

In `roles/traefik/templates/traefik.toml.j2`  there is a line

    networkInterface = "eth0"

In my case I don't have eth0.  I changed this value on the machine itself and
everything started working.

    networkInterface = "enp1s0"

The next problem is getting to this server and to a service.   When I load a
test app like hello-world I end up with a traefik front end.

hello-world.marathon.localhost

the marathon.localhost part is set in the same traefik.toml.j2 template.

if you go on the edge servers and

    curl hello-world.marathon.localhost

you get the right info.  

But how to do this from other machines?


## Setting up dnsmasq on the mac

    brew install dnsmasq


    To configure dnsmasq, copy the example configuration to /usr/local/etc/dnsmasq.conf
    and edit to taste.

      cp /usr/local/opt/dnsmasq/dnsmasq.conf.example /usr/local/etc/dnsmasq.conf

    To have launchd start dnsmasq at startup:
      sudo cp -fv /usr/local/opt/dnsmasq/*.plist /Library/LaunchDaemons
      sudo chown root /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist
    Then to load dnsmasq now:
      sudo launchctl load /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist
    ==> Summary
    🍺  /usr/local/Cellar/dnsmasq/2.75: 7 files, 512K
    larry@larrysMac$:/etc$ 



After doing what they say.. I also added the wildcard A records to /usr/local/etc/dnsmasq.conf

    address=/edge/172.16.222.16

_Note_ this means only edge01 172.16.222.16 is getting calls for the edge domain.
I tried

I need to try adding another for edge02 and see if it at least fails over.  
It doesnt because there are no health checks.  I tried

    address=/edge/edgepool

where `/etc/host` had edgepool associated with edge01 and edge02. This didn't
work either and dnsmasq would not start becasue of the bad ipaddress (edgepool)


With each experiement I restarted dnsmasq

     sudo launchctl unload /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist
    sudo launchctl load /Library/LaunchDaemons/homebrew.mxcl.dnsmasq.plist

I also edited the traefik config /etc/traefik/traefik.toml
and changed `marathon.localhost` to

    domain = "marathon.edge"

the `systemctl stop traefik` and `systemctl start traefik`

Now if you look at the traefik web ui you should be seeing names like hello-world.marathon.edge

and those should resolve in your browser.



But what about when your application has several ports?  So admin and main.

Also how about minecraft?  can you proxy something other than websites?  
db?

------

# Is Everything Working?  

------

## Where are the logs going?

docker logs are going to Syslog.  

Syslog is going to logstash.

from `roles/logstash/tasks/main.yml`

    - name: authorize logstash syslog port
      sudo: yes
      shell: semanage port -a -t syslogd_port_t -p tcp 1514
      when: selinux_syslog_port_check.rc is defined and selinux_syslog_port_check.rc != 0
      tags:
        - logstash

    - name: forward all logs from rsyslog to logstash
      sudo: yes
      lineinfile:
        dest: /etc/rsyslog.conf
        line: '*.* @@localhost:1514'
      notify:
        - restart rsyslog

If you look at roles/logstash/README.rst you can send it to a lot of places.
But by default I think all are off. Here are the options for output:

  * stdout
  * elasticsearch
  * kafka




## Where is Collectd going?

Some observations:

  * collectd has a network plugin and every one is setting server to localhost and
port 25826.    
  * Syslog is getting some of the messages but only at the err level.
  * And collectd is collecting stats from its docker containers.  
  * collectd is also installed for
    * zookeeper
    * mesos-master
    * mesos-slave
    * marathon

https://collectd.org/wiki/index.php/Networking_introduction


## WHERE IS CONSUL USER CREATED?  in Install Consul?  

Consul user needs to have a shell.

## Marathon

Are marathon health checks becoming consul health checks?

If Consul thinks its not healthy, does marathon get notified?
