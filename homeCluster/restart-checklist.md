# Restart Cluster

## HARD Turn them off without warning.

## Consul

Consul is the first thing to check. On the control hosts check `/var/lib/consul/raft/peers.json`.
if it contains `null` then you are not going to get a leader elected.   First stop Consul..

    systemctl stop consul

Then replace the `null` in `peers.json` with:

    ["172.16.222.6:8300","172.16.222.7:8300","172.16.222.8:8300"]

This is the list of the 3 control nodes. This has to be done on the `peers.json` on all 3 servers.

Then start it again.

    systemctl start consul


This is all described in https://github.com/hashicorp/consul/issues/993

Basically each consul server politely removed itself from the cluster.



Once that is working.. you can get to the web ui even if mantlui is down.  its at

    https://control01:8500/ui

Now you can see the distributive checks that are failing.

If there a lot of messed up stuff. One thing to try is a rolling restart of the control servers.

## /etc/resolv.conf

This should have:

    nameserver 127.0.0.1

If you edit it it will imediately start using dnsmasq and consul. Look at the consul ui and see a node
that is green.  do a dig on that node

    dig edge01.node.consul

If you get back an ahswer then you know that dnsmasq is forwarding to consul

These values will be overwritten by Network Manager at some point.  You need to figure out how network
manager is getting those values in there.

## Distributive checks


The distributive checks are in the /etc/distributive.d directory.  Look at the ones that are failing
in the Consul UI (`https://control01:8500/ui`) and look at the details in the json.

In my case the Mantlui healthchecks were failing.  So it checks for the existance of the image.. and then checks
that the ports are listening.

In my case the docker image was there, but no container was running.

    sudo docker images
    sudo docker ps
    sudo docker ps -a

I looked in `/etc/systemd/system` for a service file. Since most things are set up as a service.   Then I
went and looked at the ansible install commands. It is a service, placed in
/usr/lib/systemd/system/nginx-mantlui.service.

    systemctl status nginx-mantlui

Shows it failed.  Well with the network all fixed..

    systemctl start nginx-mantlui

ahhh. all green in the consul ui.  Browse to 'https://control01/ui'  and you get the mantlui







All systems

enabled - active

    sudo systemctl status chronyd

docker

    sudo docker ps

Control units should show logstash, mantlui and 3 nginx-consul containers.   Workers should show
 one logstash and one nginx-consul units.



# Check Hardaware

Resource01 lost connectivity.  I can't figure out what is up with that.

Logging in everyhing looks fine.  Lights blinking on the device and switch.

I looked through the `journalctl -b`  Entries since boot.  And didn't see any problems except the services
coming on and wanting access to the internet.

 I found http://unix.stackexchange.com/questions/83273/how-to-diagnose-faulty-onboard-network-adapter

On centos7 ethtool is installed.

 * Switched out the cable.  Used a different switch port.
 * confirmed config info

        ip route
   returned with:

        default via 172.16.222.1 dev enp0s25
        169.254.0.0/16 dev enp0s25 scope link metric 1002
        172.16.222.0/24 dev enp0s25 proto kernel scope link src 172.16.222.11
        172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.32.1

   tells me that the gateway is 172.16.222.1 and the 3rd line is my ip.  Which is what shows up for
   enp0s25 when I do `ip addr`.  Fourth line is docker.  The second line is zeroconf route.
   See here for a little discussuion of what it is https://linuxstgo.wordpress.com/fedora-16/disable-the-zeroconf-route/
   He was also disabling it but he never mentioned why.  I think that is fine and it exists on working
   systems.

 * did see any messages about it in dmesg  with `sudo cat /var/log/dmesg | grep enp0s25`
 * ran `sudo -i ethtool enp0s25` and got back link detected: yes along with a lot more.
 * also ran `sudo -i ethtool -S enp0s25` and didn't see any problems.

Here is a another [simple network troubleshooting link](http://www.linuxhomenetworking.com/wiki/index.php/Quick_HOWTO_%3a_Ch04_%3a_Simple_Network_Troubleshooting#.VvNaPxIrJ-U)

Its really quite long.  has some centos7 and mostly not systemd ways. but from those cllands you can figure out the
alternatives.

    sudo iptables -L

is a handly one.