# DCOS Install on Centos7

Following the setup of [Centos 7.2 on vms](notes-on-centos7-bridged-vm.md)
and [adding docker](notes-on-Centos7-docker.md)
we now install DCOS based on [Their DCOS on Centos7 via GUI page](https://dcos.io/docs/1.8/administration/installing/custom/gui/)

ssh to centos on the dcos-boot instance. 

    curl -O https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh
    sudo bash dcos_generate_config.sh --web -v
    
Once ot shows that the web site is waiting on :9000, use a browser to 
hit that 9000 port on that machine.  I was not ON that VM so I use the IP and
not localhost. 

 * Master Private IP List: 172.16.222.120
 * Agent Private IP List: 172.16.222.125
 * Agent Public IP List: 172.16.222.135
 * Master Public IP: 172.16.222.120
 * ssh username: centos
 * ssh listening Port: 22
 * Private SSH Key: uploaded my id_rsa
 * Upstream DNS Servers: 8.8.8.8, 8.8.4.4
 * Send telemetry: checked
 * Enable Authentication : checked (note this adds the oath loging form google and github to cluster)
 * Ip Detect Script:  See next discussion. 
 
For the IP detect script we need to write something that is going to work 
for this infrastructure. 

The [instructions for ip detect script](https://dcos.io/docs/1.8/administration/installing/custom/advanced/#ip-detect-script)
give a nice one for IP of an existing interface. 

    #!/usr/bin/env bash
    set -o nounset -o errexit
    export PATH=/usr/sbin:/usr/bin:$PATH
    echo $(ip addr show eth0 | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)

as luck would have it, on these vms it is always `enp0s3` which I discovered
with: 

    nmcli con

So the final script

    #!/usr/bin/env bash
    set -o nounset -o errexit
    export PATH=/usr/sbin:/usr/bin:$PATH
    echo $(ip addr show enp0s3 | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)

is good for this, but will have to be modified if I start bringing in the 
NUCs as they are. 

I put this script in ~/src/sophia/sophia/devops/ip-detect-script.sh

So then I loaded that and ran the preflight check.  

Preflight check came back with Port 53 not open.  

### Selinux disable

Nice [selinux setting discussion](https://www.rootusers.com/how-to-enable-or-disable-selinux-in-centos-rhel-7/)

Edit `/etc/selinux/config` and change `SELINUX=enforcing` to `SELINUX=disabled`  or permissive if you want
to figure out the logs for a future move to enforcing.

### Network Clean up

Searching on the error `Checking if port 53 (required by spartan) is in use: FAIL ` came back with 
some hits about removing dnsmasq.  

##### firewalld

There was also a discussion about firewalld in the [dcos systems requirement doc](https://dcos.io/docs/1.8/administration/installing/custom/system-requirements/#agent-nodes)
which pointed to Firewalld problems with Docker.  That [docker page](https://github.com/docker/docker/blob/v1.6.2/docs/sources/installation/centos.md#firewalld)
really it suggests that they can live together but it doesn't look like that is true. 

When I did: 

    $ systemctl status firewalld
    ● firewalld.service - firewalld - dynamic firewall daemon
       Loaded: loaded (/usr/lib/systemd/system/firewalld.service; enabled; vendor preset: enabled)
       Active: active (running) since Thu 2017-02-09 21:13:27 GMT; 2h 41min ago
         Docs: man:firewalld(1)
     Main PID: 598 (firewalld)
       CGroup: /system.slice/firewalld.service
               └─598 /usr/bin/python -Es /usr/sbin/firewalld --nofork --nopid
    
    Feb 09 22:47:16 dcosboot firewalld[598]: WARNING: COMMAND_FAILED: '/usr/sbin/iptables -w2 -t nat -C POSTROUTING -s...ailed:
    Feb 09 22:47:16 dcosboot firewalld[598]: WARNING: COMMAND_FAILED: '/usr/sbin/iptables -w2 -t nat -C DOCKER -i dock...ailed:
    Feb 09 22:47:16 dcosboot firewalld[598]: WARNING: COMMAND_FAILED: '/usr/sbin/iptables -w2 -D FORWARD -i docker0 -o...ailed:
    Feb 09 22:47:16 dcosboot firewalld[598]: WARNING: COMMAND_FAILED: '/usr/sbin/iptables -w2 -t filter -C FORWARD -i ...ailed:
    

Which doesn't look very good. So.. 

    systemctl stop firewalld
    systemctl disable firewalld

As suggested in the requirements page.  Besides.. I probably would have had to configure each ip to 
make it work.  Given the docker complaint. I'll leave that futzing for another layer. 

### Clearing Port 53 on Virtualbox Bridged VM

After doing this it still showed that port 53 was blocked and yes `yum list installed | grep dns` does
show that dnsmasq is installed but how do I know if it is listening. 

###### What is Listening on Port 53

First I checked the service (`systemctl status dnsmasq`) and it was down so:  

    sudo systemctl start dnsmasq
    
let do an error that `dnsmasq: failed to create listening socket for port 53: Address al...n use`    
    
So something is using 53 but it doesnt seem to be dnsmasq like the warnings.  
    
As it turns out netstat is installed on these vms but lets look around at the new ss.

A good [primer on ss for netstat users](https://www.nixpal.com/netstat-ss-and-rhel-7-centos/)

But when you start looking for answers.. netstat comes through. I'm using sudo to get to the program names and 
pids.   

    [centos@dcosboot ~]$ sudo netstat -tulpn | grep 53
    tcp        0      0 192.168.122.1:53        0.0.0.0:*               LISTEN      2297/dnsmasq        
    udp        0      0 192.168.122.1:53        0.0.0.0:*                           2297/dnsmasq 
    
NOTE: vanila centos 7.3 1611 does not have netstat, so this still needs he `ss` version.

So it is dnsmasq.. but its not one run by systemctl. 
 
     [centos@dcosboot ~]$ ps aux | grep 2297
     nobody    2297  0.0  0.0  15544   884 ?        S    04:39   0:00 
        /sbin/dnsmasq --conf-file=/var/lib/libvirt/dnsmasq/default.conf 
        --leasefile-ro --dhcp-script=/usr/libexec/libvirt_leaseshelper

So looking up libvirt. Looking around, libvirt is being used for my bridge and it is starting up dnsmasq 
to handle dhcp locally in a NATed bridge.  IE. Virtualbox's bridge to the host's internet.

Looking at all the services.. with `systemctl` no parameters.. we find

    [centos@dcosboot ~]$ systemctl status libvirtd
    ● libvirtd.service - Virtualization daemon
       Loaded: loaded (/usr/lib/systemd/system/libvirtd.service; enabled; vendor preset: enabled)
       Active: active (running) since Fri 2017-02-10 04:39:00 GMT; 1h 20min ago
         Docs: man:libvirtd(8)
               http://libvirt.org
     Main PID: 950 (libvirtd)
       Memory: 23.4M
       CGroup: /system.slice/libvirtd.service
               ├─ 950 /usr/sbin/libvirtd
               ├─2297 /sbin/dnsmasq --conf-file=/var/lib/libvirt/dnsmasq/default.conf --leasefile-ro --dhcp-script=/usr/libex...
               └─2298 /sbin/dnsmasq --conf-file=/var/lib/libvirt/dnsmasq/default.conf --leasefile-ro --dhcp-script=/usr/libex...
    
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: compile time options: IPv6 GNU-getopt DBus no-i18n IDN DHCP DHCPv6 no-Lua T...t auth
    Feb 10 04:39:07 dcosboot dnsmasq-dhcp[2297]: DHCP, IP range 192.168.122.2 -- 192.168.122.254, lease time 1h
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: reading /etc/resolv.conf
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: using nameserver 2001:558:feed::2#53
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: using nameserver 2001:558:feed::1#53
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: using nameserver 75.75.76.76#53
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: using nameserver 75.75.75.75#53
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: read /etc/hosts - 2 addresses
    Feb 10 04:39:07 dcosboot dnsmasq[2297]: read /var/lib/libvirt/dnsmasq/default.addnhosts - 0 addresses
    Feb 10 04:39:07 dcosboot dnsmasq-dhcp[2297]: read /var/lib/libvirt/dnsmasq/default.hostsfile
    
In order for this to work we absolutely must have access to 53 for MesosDNS, which is going to handle 
dynamic dns is all the submitted services. 

##### How to get around Libvirt dnsmasq

THis convo from 2012.. 
https://www.redhat.com/archives/libvirt-users/2012-September/msg00061.html

Leads deep deep past what I can grok.  So before diving in... What else can I do... 

I could just reinstall my NUCs and then I wouldn't have VMs at all.  But lets think a minute. 

This link shows how to limit the global dns.. which woudl be mesosdns.  https://wiki.libvirt.org/page/Libvirtd_and_dnsmasq
This will not get me out of the problem of the precheck and I'd have to modify 
mesosdns configuration.  Something I haven't even succeeded in doing.

  
  

### NTPd Setup  

This is also needed by DCOS.  

    timedatectl set-ntp 1

turns on chronyd which is the newer ntpd.    

    timedatectl 

gives status

    timedatectl set-ntp 0 

turns it off. 

    systemctl status chronyd

shows the status of the service. Which in this case is active and enabled as a result of set-ntp 1


# Feb 11 Attempt at DCOS install

THis is on the 6 nucs.  Got way farther now that I am using docker 1.11.2 (doh, read the docs)

but failed still, this time with 

    FAIL (devicemapper, /dev/loop0)

Searching on this, ends up showing up a docker issue, a dcos bug in 1.8.0 that presumably 
was fixed.  Here is part of a convo, from [docs chat log 7/4/2016](http://inscriptly.com/dcos/general/2016-07-04/3)


    mochin 2016-07-04 11:06:15
    Does remember what this error means when installing the open DC/OS via cli "FAIL (devicemapper, /dev/loop0)"
    
    activatedgeek 2016-07-04 11:07:41
    @mochin: You should use the OverlayFS Docker storage driver.
    
    @mochin: Just add/update this line DOCKER_OPTS="--storage-driver=overlay” to /etc/default/docker and restart docker service.
    
    See https://dcos.io/docs/1.7/administration/installing/custom/system-requirements/install-docker-centos/

Now this was back in July.. looking at /etc/default there is no docker file there.  So before just adding it, let me check 
what systemd is actually doing.  looking in `/etc/systemd/system`  there is a `docker.service.d` directory with an 
`override.conf` file with:

    [Service]
    Restart=always
    StartLimitInterval=0
    RestartSec=15
    ExecStartPre=-/sbin/ip link del docker0
    ExecStart=
    ExecStart=/usr/bin/docker daemon --storage-driver=overlay -H fd://

but when I look at:
    
    systemctl status docker
    ● docker.service - Docker Application Container Engine
       Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
      Drop-In: /etc/systemd/system/docker.service.d
               └─override.conf
       Active: active (running) since Sat 2017-02-11 07:39:54 PST; 52min ago
         Docs: https://docs.docker.com
     Main PID: 19117 (docker)
       CGroup: /system.slice/docker.service
               ├─19117 /usr/bin/docker daemon -H fd://
               └─19123 docker-containerd -l /var/run/docker/libcontainerd/docker-containerd.sock --runtime docker-runc --start-time...

which suggests it applies the override but the command  `/usr/bin/docker daemon -H fd://` does not include 
the `--storage-driver=overlay`?

So which one is it using?  

    [centos@control02 ~]$ sudo docker info
    Containers: 0
     Running: 0
     Paused: 0
     Stopped: 0
    Images: 0
    Server Version: 1.11.2
    Storage Driver: devicemapper
     Pool Name: docker-253:0-67181095-pool
     Pool Blocksize: 65.54 kB
     Base Device Size: 10.74 GB
     Backing Filesystem: xfs
     Data file: /dev/loop0
     Metadata file: /dev/loop1
     Data Space Used: 11.8 MB
     Data Space Total: 107.4 GB
     Data Space Available: 52.12 GB
     Metadata Space Used: 581.6 kB
     Metadata Space Total: 2.147 GB
     Metadata Space Available: 2.147 GB
     Udev Sync Supported: true
     Deferred Removal Enabled: false
     Deferred Deletion Enabled: false
     Deferred Deleted Device Count: 0
     Data loop file: /var/lib/docker/devicemapper/devicemapper/data
     WARNING: Usage of loopback devices is strongly discouraged for production use. Either use `--storage-opt dm.thinpooldev` or use `--storage-opt dm.no_warn_on_loop_devices=true` to suppress this warning.
     Metadata loop file: /var/lib/docker/devicemapper/devicemapper/metadata
     Library Version: 1.02.135-RHEL7 (2016-09-28)
    Logging Driver: json-file

It is using devicemapper, and now I know why `/dev/loop0` meant change the storage-driver in docker. 

I did a `journalctl -b` to look at whats happened since last boot.  While the docs say you need to have docker on. The log
shows that the preflight creates the overide file, then installs docker (which in my case is already installed) and then 
emables it (which in my case is already enabled).  Not to mention that the unit is cached and will require a reload. In 
otherwords the DCOS install assumes you DONT have docker installed on the target machines. It complains if its not on
the boot machine though... 

I rebooted and now: 

    [centos@control02 ~]$ systemctl status docker
    ● docker.service - Docker Application Container Engine
       Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
      Drop-In: /etc/systemd/system/docker.service.d
               └─override.conf
       Active: active (running) since Sat 2017-02-11 08:48:20 PST; 26s ago
         Docs: https://docs.docker.com
      Process: 990 ExecStartPre=/sbin/ip link del docker0 (code=exited, status=1/FAILURE)
     Main PID: 1018 (docker)
       Memory: 49.1M
       CGroup: /system.slice/docker.service
               ├─1018 /usr/bin/docker daemon --storage-driver=overlay -H fd://
               └─1145 docker-containerd -l /var/run/docker/libcontainerd/docker-containerd.sock --runtime docker-runc --start-timeout 2m
               
              
               
Retry preflight works. Deploy.. postflight..  Login, install marathon from universe... 

And I am in :) 