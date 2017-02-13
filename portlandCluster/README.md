# Portland Cluster

Looking at building out the cluster from scratch.   Lots of new tech going on.

Several things going into thinking about this on Dec 14, 2016:
 
Devops Tech
 
 * Mantl is no longer being maintained.    
 * Asteris LLC team has moved on and created converge to do this.

Cluster Tech

 * DCOS is a real thing now and covers most of it. 
 * Kubernetes might be a better thing.
 * look again at Nomad? 
 * I am way farther down the hadoop learning curve
 * Spark too.  It would be nice to have both Spark 1.6 and 2.0 lines
 * Kafka does not seem go away

Admin

 * Docker for Mac is a thing
 * Slacki has this interesting kickcstart wrapper, better than Cobbler
 * I'd like to finally solve the whole internal DNS problem I have.
 * [IP per container like Contiv](http://contiv.github.io/)
 * Need to start using my Meraki Z1

## Router 1.0
 
 * Using Verizon Router  user admin, pass local easy shared
 * changed gateway address to `172.16.222.1`
 * DHCP starts at 100
 * DHCP lease time changed to 5 weeks. 
 * once that was set up we took out the LinkSys and pluggged the 
 Verizon router directly into the 24 port switch in the NUC Cluster.
 
## DCOS 1.0  Vagrant Cluster
 
 * Systems is on Sir Muck - `SirMuck` Followed the directions at `https://github.com/dcos/dcos-vagrant/` 
 * `/Users/lmurdock/software` is base directory where I ran  `git clone https://github.com/dcos/dcos-vagrant` 
 
The bitch with this cluster is that it is tiny and can't handle much.  If the machine 
is rebooted, the zookeeper will generally fail and then the whole thing is 
down.  You can always pull it back up by doing `vagrant destroy` 
and `vagrant up`

## DCOS 2.0 Virtual Boxes Cluster

This system is going to create 2 6GB Ram 2 Core machines on `Puck` and `Peek`.  In their new roles
I made them mever go to sleep, and set them to start up on power off.  This is in Mac settings 
"energy saver".

The machines created are: 

On Puck

 * 172.16.222.119 DCOS-Boot
 * 172.16.222.120 DCOS-Master
 
On Peek
 
 * 172.16.222.125 DCOS-PubAgent
 * 172.16.222.135 DCOS-PrvAgent


These were made with 2 core, 6GB of ram and Centos 7.2 (1611)  as described 
[here](notes-on-centos-bridged-vm.md) .

This failed as a result of the fact that the bridged network uses dnsmaaq on port 53 to do bridged networks 
and the preflight check fails because 53 is needed for MesosDNS.  There may be a work around.. and it would be good to 
have since you could add capacity from a room full of macs... but another time. 

## DCOS 3.0 Nucs 

Then I tried to clear off my Nucs that had mantl.io, but the preflight failed when it said I already
had dcos installed.. They do share a lot of the same packages.

The fist parts of [Notes on Centos7 Nucs](notes-on-centos7-nuc.md) from the start of the file to 
"Back to the begining""

## DCOS 4.0 NUCs clean install Centos 7.3 (1611)

The section "Back To The Begining" to the end in [Notes on Centos7 Nucs](notes-on-centos7-nuc.md) covers
what it took to get a working DCOS environment on my NUCs. 

Following installation I did some [notes on tutorials](notes-on-dcos-tutorial101.md)









