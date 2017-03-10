# Installing Docker on Centos7

Docker on Centos7 has been a complicated thing in the past.  If I run 
into stuff I'll add info here.  I am guessing the official info is 
fine for my VM based install. 

## Docker on Centos 7.2 VirtualBox VM

Following this doc.  https://docs.docker.com/engine/installation/linux/centos/

Make sure to check the systems requirements page for your verison of DCOS.. for 1.8 that is. 
https://dcos.io/docs/1.8/administration/installing/custom/system-requirements/

In it, they only support Docker 1.7.x to 1.11.x.  Current version of Docker is 1.13

And using the Docker Repository. 

    sudo yum -y remove docker
    sudo yum -y remove docker-selinux
    
There also seems to be a `docker-common` that can also be a problem.  On my centos 7.2 there was a docker-common 
that kept me from installing docker-engine below. 
    
neither of these are on the image created with [Centos bridged VM Doc](notes-on-centos7-bridged-vm.md)

    sudo yum install -y yum-utils

was already on there. 

    sudo yum-config-manager \
        --add-repo \
        https://docs.docker.com/engine/installation/linux/repo_files/centos/docker.repo
        
Saved in '/etc/yum.repo.d/docker.repo'

I did not turn on testing repo.   I want a solid stable docker as we are mixing enough 
things together already. 

    sudo yum makecache fast

    
you need to chose a version that is compatible with DC/OS in the requirements page 
displayed above, for the version I am installing, 1.11 was the last version
supported.  [Instructions for installing a version](https://www.centos.org/forums/viewtopic.php?t=16778)

#todo this needs to be about docker
    yum list --showduplicates docker-engine
    
gets you a long list with entries like:
    
    docker-engine.x86_64     1.10.3-1.el7.centos      docker-main
    docker-engine.x86_64     1.11.0-1.el7.centos      docker-main
    docker-engine.x86_64     1.11.1-1.el7.centos      docker-main
    docker-engine.x86_64     1.11.2-1.el7.centos      docker-main
    docker-engine.x86_64     1.12.0-1.el7.centos      docker-main
    docker-engine.x86_64     1.12.1-1.el7.centos      docker-main
    docker-engine.x86_64     1.12.2-1.el7.centos      docker-main

Sinced 1.11.2 is the most recent said to be compatible.

    
    sudo yum -y install docker-engine-1.11.2-1.el7.centos   

    sudo systemctl start docker
    sudo systemctl enable docker
    
I added that last one to have docker startup on restart. 

After all this you can check it with:

    [centos@dcosboot ~]$ sudo systemctl status docker
    ● docker.service - Docker Application Container Engine
       Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
       Active: active (running) since Thu 2017-02-09 22:47:22 GMT; 19s ago
       
       
In particular note that, enabled.  preset is disabled.  and It is active. 

## Docker Compose

Oddly, this isnt' really a part of Docker unless you have docker for Mac
or that os that is not *nix, I forget the name..

[Here is the official page.](https://github.com/docker/compose/releases)



