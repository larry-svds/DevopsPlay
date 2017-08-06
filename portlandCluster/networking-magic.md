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

http://www.binarytides.com/linux-ss-command/

##### Ubuntu 16.04

The mac ones work.

# SSH

#### How to force ssh login via public key authentication

In `/etc/ssh/sshd_config` set `PasswordAuthentication no` and then also:

    RSAAuthentication yes
    PubkeyAuthentication yes

then reload sshd which old school is `sudo /etc/init.d/ssh reload` and centos7
is `sudo systemctl reload sshd`.



## How to set up an ssh tunnel

http://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html

$ ssh -L 9000:imgur.com:80 user@example.com

For example.. to bring up the checkmk interface to my localhost..

ssh -nNT -L 4343:localhost:80 ubuntu@172.31.34.161

see the options at http://linuxcommand.org/man_pages/ssh1.html

 * `n` redirects stdin from /dev/null
 * `N` doesn't execute a remote command, useful for port forwarding sessions.
 * `T` disable pseudo-tty allocation (you aren't interacting)
 * `L` local port exported. (I cant really wrap my head around -L and -R but
    `L` brings the far away port here.. and `R` puts my laptop port there.


(side note in case I actually am doing this.. http://localhost:4343/svds/omd/)

The black magic of ssh/ SSH can do that?  https://vimeo.com/54505525

ssh -R pushes a port to the other.

ssh has an interactive mode.

##### Dynamic Port Forwarding

Socks proxy to a local port.  tunnel every connection through it.

Simple VPN in a pinch.

    ssh -D 5555 bastion

    ssh -fNn -D 5555 bastion

    curl --socks5-hostname localhost:5555 -I rubygems

##### X11 Forwarding

##### Agent forwarding

    ssh -A sshtalk.in

when you don't have the private key on the local one but
but you do at sshtalk.  So -A means get the keys
from sshtalk.in

##### Run a remote command

    ssh my-server.com -- hostname my-server.com
    ssh my-server.com -- whoami

    ssh root@my-server.com -- cat /var/log/secure | tee secure.log | wc -l
    cat ./secure.log | grep -w "root" | wc -l

##### forcing remote command execution

You can prefix ssh public keys with options in the ~/.ssh/authorized_keys file.
So in the authorized keys file, before the ssh-rsa part, you have

    command="echo=\"You tried to run ${SSH_ORIGINAL_COMMAND}\"" ssh-rsa AAAAblah blah


One such option is the `command="any comand here""`

When you run `git clone git@github.com:super/project.git` what is actually
being run is    `ssh git@github.com -- git-recieve-pack super/project.git

Github prefixes everybody's keys with a `command="..."` line that only
allows white-listed commands to be executed.

// #todo There might be something interesting here https://github.com/bjeanes/authorized_keys


##### SSHConfig

Lots goes in her

    Host github github.example.com
      User git
      ProxyCommand ssh -q bastion-east nc github %p
      IdentifyFile ~/.ssh/git.pub

    Host *.east
      ProxyCommand ssh -q bastion-east nc `echo "%h" | tr _ -` %p

    Host *.west
      ProxyCommand ssh -q bastion-west nc `echo "%h" | tr _ -` %p

    Host *
      User bjeanes
      ForwardAgent yes
      StrictHostKeyChecking no
      ServerAliveInterval 120
      Compression yes
      EscapeChar ^y

Some fun ^ stuff to figure out.  Many of this are not good to do..
but convienient.  `nc` is netcat.

What I got from Mark is

    Host localhost
        Hostname 127.0.0.1
        User larry
        IdentityFile ~/.ssh/key-svds_rsa
        ProxyCommand none

    Host old-bastion
        Hostname 52.24.216.36
        #Hostname bastion-west2.svds.io
        ProxyCommand none

    Host 172.31.*.*
      User ubuntu
      ProxyCommand ssh old-bastion nc -q0 %h %p
      IdentityFile ~/.ssh/TestSVDS.pem
    Host devops
        Hostname 172.31.18.73
        User ubuntu
        ProxyCommand ssh old-bastion nc -q0 %h %p
        IdentityFile ~/.ssh/TestSVDS.pem

    Host svds-bastion
      Hostname 52.36.196.98
      User ubuntu
      IdentityFile ~/.ssh/key-svds_rsa

    Host 10.1.*.*
      User ubuntu
      IdentityFile ~/.ssh/key-svds_rsa

##### SSHFS

Expose a remote file system as a local one using fuse.

https://github.com/libfuse/sshfs


##### Allow logins with people's github account

https://github.com/donapieppo/libnss-ato

which took a little bit of work to get compiling but otherwise works




