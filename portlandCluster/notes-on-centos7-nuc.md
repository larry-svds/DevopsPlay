# Bring the Nucs into DCOS

The nucs were set up with Mantl.io.  I want to get them over to dcos.io 
for the presumed simplicity of it. 

Instead of reinstalling.  I am going to upgrade and disable things as I go
along.  "What could go wrong" TM.

## Upgrade to Centos 7.3 1611

First thing is these are Centos 7.2 1511.  Want to upgrade them. 

The mantl repo is broken so.. 

    su
    yum upgrade --skip-broken

## Stop the mantl processes

    systemctl stop consul
    systemctl stop consul-template
    systemctl stop marathon
    systemctl stop mesos-master
    systemctl stop vault
    systemctl stop collectd
    systemctl stop consul
    systemctl stop consul-template
    systemctl stop dnsmasq
    systemctl stop docker
    systemctl stop logstash
    systemctl stop marathon
    systemctl stop mesos-master
    systemctl stop mesos-agent
    systemctl stop nginx-consul
    systemctl stop nginx-mantlui
    systemctl stop nginx-marathon
    systemctl stop nginx-mesos-leader
    systemctl stop vault
    systemctl stop zookeeper

and disable them too

But since you just killed dnsmasq.. 

you need to set dns name servers. I went and looked at the 
interface config file `/etc/sysconfig/network-scripts/ifcfg-enp0s25`
and there are nameservers in those files. I went ahead and rebooted. 
If they don't come back.. I have a lot of messing around to do. 

It did.. eventually I realize that the interfaces are not networkmanager managed. 
There for /etc/resolv.conf is not overwriten.  So.  I just deleted all 
lines and the contents of /etc/resolv.com is 

    nameserver 8.8.8.8
    nameserver 8.8.4.4
    

### How I work on 6 machines at a time. 

install tmux and then run this script. Magic.

    #!/bin/sh

    usage() {
      echo "Usage: $0 user1@host1 user2@host2 host3 host{4..6} host7 host8 [...]"
    }
    [ $# -lt 1 ] && usage && exit 1
    
    create_ssh_pane() {
      local session=$1
      local host=$2
    
      tmux has-session -t $session 2>/dev/null \
        && tmux split-window -t $session "exec ssh $host" \
        || tmux new-session -d -s $session "exec ssh $host"
    
      tmux select-layout -t $session tiled >/dev/null
    }
    
    export session="cssh-$$"
    for host in "$@"; do
      create_ssh_pane $session $host
    done
    #tmux set-window-option -t $session status off >/dev/null
    tmux set-window-option -t $session synchronize-panes on >/dev/null
    exec tmux attach -t $session

## Switch to the Docker Repo And Docker
  
    
    sudo yum -y remove docker
    sudo yum -y remove docker-selinux
    
Actually did delete repos that were being used. 

I then did the rest of the stuff in. 
[docker notes](notes-on-Centos7-docker.md)


When I went back to install DCOS we ended up with pre-flight check error of:

    Checking if DC/OS is already installed: FAIL (Currently installed)
    
Which is a full stop with DC/OS at this time. 

https://docs.mesosphere.com/1.8/administration/installing/custom/uninstall/

If you go to the two issues.. they are low priority so the following 
instructions are worth taking carefully. 

## BACK TO THE BEGINING

### Make a Thumb Drive

Start with getting a thumb drive. http://www.myiphoneadventure.com/os-x/create-a-bootable-centos-usb-drive-with-a-mac-os-x

I downloaded the DVD iso from https://wiki.centos.org/Download.  7 Was at 1611. 

    hdiutil convert -format UDRW -o CentOS-7-x86_64-DVD.img CentOS-7-x86_64-DVD.iso

did `diskutil list` and figured out that disk3 is the USB stick (which I putin a USB slot)

    diskutil unmountDisk /dev/disk3
    time sudo dd if=CentOS-7-x86_64-DVD.img.dmg of=/dev/disk3 bs=1m
    
### The Reboot and Install

On reboot, there is a menu that shows up rather quickly where it tells me that f10 
goes to boot menu. 
 
 * UEFI : USB : PNY USB 3.0 FD 1100 : PART 0 : OS Bootloader

Was the right choice. There was another entry with USB, that is the Boot Drive.   

THen you are offered a chance to install centos7, do that.  

##### Network

Set Date & Time to PST.  

So I went into the network and enabled the Ethernet and then configured it. 

Hit Configure at the bottom right. Then pick IPv4 Settings and add:

 * manual
 * Set Address(172.16.222.28), netmask (255.255.255.0) and gateway (172.16.222.1)
 * DNS Servers set to 8.8.8.8, 8.8.4.4
 * search domain to kafush.in
 * I checked "require IPv4 addressing for this connection to complete" becuase unchecking it means the connection work
even if only IP6 goes through.  I think I want it to scream louder if it cant get IPv4, I
hope that is what I am getting.  https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Installation_Guide/sn-Netconfig-s390.html

##### Drive Partitioning

There is some weirdness with various storage products that want raw partitions, so 
the standard partitioning schemas are not a good idea for this cluster. 

I went ahead and deleted existing partions and then did an automatic partions. 
It put the bulk in home .  I reduced that to 600G leaving 1200G unformated. 

 * /home 600G
 * /boot 1024M
 * /boot/efi 200M
 * / 50G
 * swap 8G

 
That leaves 1200 Gs to play with later on the 2 TB drive on 3 of my machines.  For 
the 3 that have the 500G ssds, I let it put all of it in home. 

##### Reboot and set name

    hostnamectl set-hostname resource03.kafush.in

### Other things like Bridged VM

[bridged vm notes](notes-on-centos7-bridged-vm.md)

Fixed sudo to not have password. 

Added keyless acess



### Deal with things needed by DCOS


##### NTPd Setup  

This is also needed by DCOS.  

    timedatectl set-ntp 1

turns on chronyd which is the newer ntpd.    

    timedatectl 

gives status

    timedatectl set-ntp 0 

turns it off. 

    systemctl status chronyd

shows the status of the service. Which in this case is active and enabled as a result of set-ntp 1

NOTE: If `timedatectl set-ntp 1` fails with NTP not supported.

    sudo yum install -y chrony
    sudo systemctl start chronyd
    timedatectl set-ntp 1


### Selinux disable

Nice [selinux setting discussion](https://www.rootusers.com/how-to-enable-or-disable-selinux-in-centos-rhel-7/)

Edit `/etc/selinux/config` and change `SELINUX=enforcing` to `SELINUX=disabled`  or permissive if you want
to figure out the logs for a future move to enforcing.

##### firewalld disable

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


### Get Docker up and running

Then I did all the parts in [centos7 docker notes](notes-on-Centos7-docker.md)

Postscript.. DONT put docker on.. DCOS preflight will install it.  It actually caused me trouble 
to have Docker running.

### Get DCOS up and running. 

Finally with the above (including docker) I did [notes on dcos install](notes-on-dcos-install.md) 
from "Feb 11 Attempt at DCOS install" and succeeded.

### Set /etc/hosts in all nodes with the info of the other machines. 

I don't have dns working for `kafush.in` domain.. so the low tech version 
was to add: 

    172.16.222.6 control01.kafush.in control01
    172.16.222.7 control02.kafush.in control02                         
    172.16.222.8 control03.kafush.in control03                        
    172.16.222.11 resource01.kafush.in resource01                    
    172.16.222.12 resource02.kafush.in resource02                    
    172.16.222.13 resource03.kafush.in resource03  
                  
to `/etc/hosts` on all 6 machines. 
                  
I didn't run into any problems without this, until I did something with 
[interactive pyspark shell](https://docs.mesosphere.com/1.8/usage/service-guides/spark/spark-shell/)
which is pretty much the first real thing I did on the cluster. 
 
### Do some Tutorials

And with it working I did [some tutorials](notes-on-dcos-tutorial101.md)
