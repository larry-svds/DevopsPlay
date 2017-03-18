# Network commands



## What is listening?

#### Mac OS

show all processes with names.. listening on ports.

    sudo lsof -i -P | grep  -i "listen"

this netstat doesn't show the name.  but seems a bit different list.
//#todo go into this a bit more.. Right now i am just capturing useful stuff

    netstat -atp tcp | grep -i "listen"


#### Centos 7

netstat doesn't exist in centos 7 and that fucntionality
is covered by the new `ss` command.

https://www.nixpal.com/netstat-ss-and-rhel-7-centos/


##### Ubuntu 16.04

The mac ones work.

## How to set up an ssh tunnel

http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html

$ ssh -L 9000:imgur.com:80 user@example.com

For example.. to bring up the checkmk interface to my localhost..

ssh -nNT -L 4343:localhost:80 ubuntu@172.31.34.161

(side note in case I actually am doing this.. http://localhost:4343/svds/omd/)

