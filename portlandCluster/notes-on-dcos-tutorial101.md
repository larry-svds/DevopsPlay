# Adventures in Learning DCOS

Running through some tutorials and taking some detours along the way. 

 * dc/os 101
 * simple docker

## DC/OS 101

The following is my run through [DC/OS 101](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/)

##### Install CLI

Would love to see this in brew.  For my own notes.. I followed 
[this](https://dcos.io/docs/1.8/usage/cli/install/)  placing the 
executable in `~/software/dcos` and then made it executable and soft
linked it `cd /usr/local/bin ; ln -s /Users/larry/software/dcos/dcos dcos`

    dcos auth login

comes back with a link.. I then login in with the google oath user that I 
added to my dc/os when I installed. It returned with a big token and I copy 
and pasted it to command line.. `Login successful!`

    
###### Add Another User 

Any user can add others.  Any User in the system is an admin user. 

### Explore dcos cli


Note: `dcos node log --leader` gives you log access.  Worth looking into and 
remembering.  Also after creating a task... you can see the tasks log by simply 
saying `dcos task` to find the name.. then for redis named 
task.. `dcos task log redis`

Note: `dcos service` showed services running.  Metronome is a scheduling service I had 
not seen before. 

[CLI Documentation](https://dcos.io/docs/1.8/usage/cli/)

##### [DC/OS 101 Section: Installing First Package](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/redis-package/)

In installing your first package section of the DC/OS 101 there is a long command 
for sshing into the redis task. 

    dcos node ssh --master-proxy --mesos-id=$(dcos task redis --json | jq -r '.[] | .slave_id')
    
First.. jq might not be installed on your machine.. `brew install jq` on my box (it was installed
but just sayin)

Next thing to notice is that while

    $ dcos task redis
    NAME   HOST           USER  STATE  ID                                          
    redis  172.16.222.12  root    R    redis.b6cd9b67-f159-11e6-9c0c-70b3d5800001

if you do `dcos task redis --json`  you get a ton more information. playing around 
with it you could also do this command in a more brain dead, and less "remember an equation way"

    $dcos task redis --json | grep slave_id
        "slave_id": "a2e600e1-f251-4699-a0c9-69d9b5d57f0f-S0",

copy and paste into 

    $dcos node ssh --master-proxy --mesos-id=a2e600e1-f251-4699-a0c9-69d9b5d57f0f-S0
    
Next thing is that its trying to log into the `core` user.    
 
The writer of the documentation must be using coreos, and that is apparently the default setting. 
investigating the [docs](https://dcos.io/docs/1.8/administration/access-node/sshcluster/)
you just have to add `--user=centos`  that document above also gives an alternative 
gui way to find the agent_id (called slave_id in the json for historical reasons)

    dcos node ssh  --user=centos --master-proxy --mesos-id=a2e600e1-f251-4699-a0c9-69d9b5d57f0f-S0
    
Then to get in to redis. 

    sudo docker ps
    sudo docker exec -i -t <put container id from ps here> /bin/bash
    
##### [DC/OS 101 Section: Deploying your First Application](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/app1/)

If you get curious about the weird 'redis.marathon.l4lb.thisdcos.directory' in app1.py.. it will 
be explained in the next section on service discovery.

I could not: 

    dcos marathon app add https://raw.githubusercontent.com/joerg84/dcos-101/master/app1/app1.json

but I could see it in the browser.  Got around it with 

    curl -O https://raw.githubusercontent.com/joerg84/dcos-101/master/app1/app1.json
    dcos marathon app add app1.json

So when I looked at the app

    $ dcos marathon app list 
    /dcos-101/app1  128    1     1/1    ---       ---      False      DOCKER   while true; do python $MESOS_SANDBOX/app1.py; done
    
The python program references `$MESOS_SANDBOX` which is a very interesting directory. [doc](http://mesos.apache.org/documentation/latest/sandbox/)

Looking at the app1.json:
  
    {
    "volumes": null,
    "id": "/dcos-101/app1",
    "cmd": "while true; do python $MESOS_SANDBOX/app1.py; done",
    "instances": 1,
    "cpus": 1,
    "mem": 128,
    "disk": 0,
    "gpus": 0,
    "fetch": [
      {
        "uri": "https://raw.githubusercontent.com/joerg84/dcos-101/master/app1/app1.py"
      }
    ],
    "container": {
      "docker": {
        "image": "mesosphere/dcos-101",
        "forcePullImage": false,
        "privileged": false,
        "network": "HOST"
      }
     }
    }

You see the cmd. and also the fetch.  Fetch puts the fetched file into `$MESOS_SANDBOX`

    $ dcos node ssh --user=centos --master-proxy --mesos-id=a2e600e1-f251-4699-a0c9-69d9b5d57f0f-S0
    $ sudo docker ps
    CONTAINER ID        IMAGE                         COMMAND                  CREATED             STATUS              PORTS                     NAMES
    4b47088b3a4a        mesosphere/dcos-101           "/bin/sh -c 'while tr"   About an hour ago   Up About an hour                              mesos-a2e600e1-f251-4699-a0c9-69d9b5d57f0f-S0.3ec8ea47-8c2d-48fd-a092-81bb4507e485
    $ sudo docker exec -i -t 4b47088b3a4a /bin/bash
    # echo $MESOS_SANDBOX
    /mnt/mesos/sandbox
    #ls $MESOS_SANDBOX
    app1.py  stderr  stderr.logrotate.conf	stdout	stdout.logrotate.conf
    
This is where the logs are that `dcos task log <task>` but when I tried this I got an unexpected 
behaviour worth noting.  After this.

    $ dcos task
    NAME           HOST           USER  STATE  ID                                                  
    app1.dcos-101  172.16.222.12  root    R    dcos-101_app1.047cfe48-f165-11e6-9c0c-70b3d5800001  
    marathon-user  172.16.222.12  root    R    marathon-user.c760c446-f07b-11e6-9c0c-70b3d5800001  
    redis          172.16.222.12  root    R    redis.b6cd9b67-f159-11e6-9c0c-70b3d5800001 
 
From the previous lesson.  `dcos task log redis` gave us the log for redis. So I figrured name was the 
thing.. but its not..  `dcos task log app1.dcos-101` doesnt match any task.  you have to get to the 
unique part of the id field.   So even 

    dcos task log d
    
Works becuase its unique in that list of tasks. 

##### [DC/OS 101 Section: Service Discovery](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/service-discovery/)

So remember to add `--user centos` to the `dcos node ssh` commands

once you log in. Minimal Centos does not have dig.  you can get the info you want with 

    $ getent hosts redis.marathon.mesos
    172.16.222.12   redis.marathon.mesos

It continues to ask about the services so I guess you can install dig and friends. 

    yum install -y bind-utils
    
This allowed me to go to the end of section but I got kinda lost in the named vip section. 

What helped me get the context I needed was [virtual IO Addresses doc](https://docs.mesosphere.com/1.8/usage/service-discovery/load-balancing-vips/virtual-ip-addresses/)
and looking at the web interface , under Services, redis, you do see that it is set to `redis:6379`.  If 
you hit edit you can explore what can be set up in the gui.  Additionally in the top right you 
can hit json mode and see the code you would use if submitting from the command line. 

In the doc they also show how to do it in jso for the command line. 

    {
      "id": "/my-service",
      "cmd": "sleep 10",
      "cpus": 1,
      "portDefinitions": [
        {
          "protocol": "tcp",
          "port": 5555,
          "labels": {
            "VIP_0": "/my-service:5555"
          },
          "name": "my-vip"
        }
      ]
    }

They also mention that there are portMappings or portDefinitions.  Above is PortDefinitions.  But 
redis is a docker and so has a bridged network and so its definition needs a portMappings.  

Here is the first part of the `container` section of the redis json:

     "container": {
        "docker": {
          "image": "redis:3.0.7",
          "forcePullImage": false,
          "privileged": false,
          "portMappings": [
            {
              "containerPort": 6379,
              "protocol": "tcp",
              "servicePort": 10002,
              "labels": {
                "VIP_0": "/redis:6379"
              }
            }
          ],
          "network": "BRIDGE"
        }
    

Looking for `dcos l4lb` in google suggests that this is the [minuteman distributed load balancer](https://github.com/dcos/minuteman)

##### [DC/OS 101 Section: Deploying Native Applications](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/app2/)

again I had trouble downlaoding the app2.json in the `dcos marathon app add` call but I could 

    $ curl -O  https://raw.githubusercontent.com/joerg84/dcos-101/master/app2/
    $ dcos marathon app add app2.json
    
##### [DC/OS 101 Section: Exposing Apps Publicly](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/marathon-lb/)
    
When installing marathon-lb 

    $ dcos package install marathon-lb
    We recommend at least 2 CPUs and 1GiB of RAM for each Marathon-LB instance. 
    
    *NOTE*: ```Enterprise Edition``` DC/OS requires setting up the Service Account in all security modes. 
    Follow these instructions to setup a Service Account: https://docs.mesosphere.com/1.8/administration/id-and-access-mgt/service-auth/mlb-auth/
    Continue installing? [yes/no] yes
    
You don't have to do that.. but thought I'd note it so I can look it up later and see whats up. Bottom line is, without 
a service account you marathon-lb is a big security risk. 

##### [DC/OS 101 Section: Load-balancing](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/loadbalancing/)

##### [DC/OS 101 Section: Understanding Resources](https://dcos.io/docs/1.8/usage/tutorials/dcos-101/resources/)

In the previous parts of this tutorial we have been defining the apps as /dcos-101/app1 and app2 
and it wasn't clear why there was a '/' now it appears that you can refer to the dcos-101 part as a 
group and scale the whole group.  

Here is another interesting point.. 

> Add nodes or scale the app to a level at which resources are available dcos marathon app 
 update /dcos-101/app2 --force instances=1. Note you have to use the --force flag here as 
 the previous deployment is ongoing.

Also an interesting discussion about how apps that run out of memory might not be obvius from the DCOS 
console becuase they just keep rebooting.  Suggests logging locally and checking `journald`.

## [Deploying a Docker-based Service to Marathon](https://dcos.io/docs/1.8/usage/tutorials/docker-app/)

This tutorial ends without checking if it worked.  If you ran DC/OS 101 before the docker one, then 
marathon lb was siting on port 80.  

To fix this you have to change the host port to something not being used.. say 8888

This version of the tutorial put placed the container on the public-agent.  Might be more interesting 
to see if we can get it behind the marthon-lb.. 

To do this. Change the acceptedResouceRoles to "slave_private" and change the port mapping to feed 
out 10098. I picked a # between 10000 and 10100 becasue of the way Marathon-LB was configured. One 
more thing you have to do is set a label for "HAPROXY_GROUP": "external" so that Marathon-LB will
serve it out. I'm not sure why "requirePorts" : false works...

    {
        "id": "nginx","
        "container": {
        "type": "DOCKER",
        "docker": {
              "image": "catfishlar/simple-docker",
              "network": "BRIDGE",
              "portMappings": [
                { "containerPort": 80,
                  "protocol": "tcp",
                  "servicePort" : 10098
                }
              ]
            }
        },
        "labels": {
          "HAPROXY_GROUP": "external"
        },
        "requirePorts": false,
        "instances": 1,
        "cpus": 0.1,
        "mem": 64
    }

I had a lot of trouble with getting the right ports to work.  What often happened when it was configured
incorrectly.. like when hostPort was 80, is it would just wait. There is more I have to understand 
about this. 

I am choosing servicePorts because it does have to be unique across the cluster if it is being feed out
to external from the marathon-lb.  

