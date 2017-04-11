# notes on virtualbox for nuodb tests

I grabbed a centos box and created the clones per
[notes on centos7 bridged vm](../portlandCluster/notes-on-centos7-bridged-vm.md)


This is different than a typical vagrant setup in that I set them up
with known IPs and also gave then bridged hosts.  This allows me to
get to it from other machines on the network.

One advantage of this is that I can set this up on one of my desktops and
then hit it from a client on my laptop.  Thus I don't actually have to
bring it up and down to do other work.

If you don't do the steps to reserve the IPs in your router, then you
just have to figure out what IPs the instances got from DHCP and those will
stay the same as long as the cluster is up and running.

THey tend to go back to the same IPs on reboot.. but its not forever.

So I went through all the steps above, minus the guest additions and then
did a full clone to a vm I am calling C 7.3 NuoDB.

The steps that go into this VM are based on the steps defined in.

[nuodb Scale Out with the New NuoDB Community Edition Release](https://www.nuodb.com/techblog/scale-out-new-nuodb-community-edition-release)

#### Add Oracle Java JRE 1.8

I am going to go ahead and install the jdk. We want oracle jdk.  But this
is not the standard yum java so we are going to install it in /opt and
so this page is current https://tecadmin.net/install-java-8-on-centos-rhel-and-fedora/#

    sudo su -
    cd /opt
    wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u121-b13/e9e7ea248e2c4826b92b3f075a80e441/jdk-8u121-linux-x64.tar.gz"

    tar xzf jdk-8u121-linux-x64.tar.gz
    rm jdk-8u121-linux-x64.tar.gz

Then add it to alternatives and turn it on.

    alternatives --install /usr/bin/java java /opt/jdk1.8.0_121/bin/java 2
    alternatives --config java

config is going to show you the ones that exist and ask you to pick the
number for the version of java you want.  Note 7.3 already comes with a nice
current version of java 1.8 but NuoDB is specifying Oracle.  So pick the
new one.  Once you are done.. you can check that you in fact are using
oracle java ( HotSpot(TM) )

    [root@osboxes opt]# java -version
    java version "1.8.0_121"
    Java(TM) SE Runtime Environment (build 1.8.0_121-b13)
    Java HotSpot(TM) 64-Bit Server VM (build 25.121-b13, mixed mode)



#### Disable Transparent Huge Pages (THP)

For a `systemd` system, the instructions on the Nuodb page are not quite
systemd'ish.  So I am following the [a better set of instruction](https://blacksaildivision.com/how-to-disable-transparent-huge-pages-on-centos)

Create following file:

    sudo vi /etc/systemd/system/disable-thp.service

and paste there following content:

    [Unit]
    Description=Disable Transparent Huge Pages (THP)

    [Service]
    Type=simple
    ExecStart=/bin/sh -c "echo 'never' > /sys/kernel/mm/transparent_hugepage/enabled && echo 'never' > /sys/kernel/mm/transparent_hugepage/defrag"

    [Install]
    WantedBy=multi-user.target

Save the file and reload SystemD daemon:

    sudo systemctl daemon-reload

Than you can start the script and enable it on boot level:

    sudo systemctl start disable-thp
    sudo systemctl enable disable-thp

#### Install Nuodb

Download the RPM at https://www.nuodb.com/dev-center/community-edition-download
to the centos7 box and then:

On April 8 this was:
    https://www.nuodb.com/modals/nojs/nuodb_info_modal_form/file/nuodb-ce-2.6.1.5.x86_64.rpm /2.6.1%20Linux%20.rpm

    # sudo rpm -i nuodb-ce-2.6.1.5.x86_64.rpm
    NOTE: The NuoDB Broker is not configured.

    Please set a domain password in /opt/nuodb/etc/default.properties,
    then run 'service nuoagent start' to bring up the Broker.

#### change domain password


    sudo vi /opt/nuodb/etc/default.properties

uncomment `#domainPassword = ` and change to `domainPassword = bird`

assuming you want the domain password to be `bird`...

#### Turn off the firewall

    sudo systemctl stop firewalld
    sudo systemctl disable firewalld

check with

    sudo systemctl status firewalld

If the firewall is up it will block 48004 and other ports.  You COULD
figure this out.  Maybe you even should..  I messed with
punching holes for individual ports.  but dynamically if you start more than one te
or sm on a broker it is going to increment the port, from 48004 to 48005 etc.

Working out the port stuff is going to be important for Docker as well.

Firewalld is rhel/centos 7 for iptables, sort of.

#### NOW CREATE YOUR LINKED CLONES

At this point you can create the linked clones for the number of machines
you are going to have in your cluster.

Make

#### Create an Storage Manager (SM)

Create a location for the database.

    mkdir /tmp/databases
    sudo chown nuodb.nuodb /tmp/databases

THe run the manager.

    /opt/nuodb/bin/nuodbmgr --broker localhost --password bird

will bring up a prompt and you type.. a lot..

    nuodb [domain] > start process sm archive /tmp/databases host 172.16.222.214 database testdb initialize true
    Process command-line options (optional):

This creates a sm (storage manager) at the location /tmp/database
on that specific host with database testdb and intialize it.

When asked for options, just hit enter to take the defaults.

#### Adding Another VM to the cluster

    sudo vi /opt/nuodb/etc/default.properties

uncomment `#domainPassword = ` and change to `domainPassword = bird`

like before (it is probably already done.)

but then add

    peer = <name or IP of first node>':'<port it is listening on>'

so for example.

    peer = sm1:48004

where `172.16.222.214 sm1` is a line in `/etc/host` and that is the first
node that was started. The port 48004 is the default broker port.

You then run

    sudo service nuoagent start

You should get back an `OK`, or an error.. I was getting errors becuase
the firewall was blocking.

You can see that it has joined the right group with

    /opt/nuodb/bin/nuodbmgr --broker localhost --password bird

    nuodb [domain] > show domain hosts

    [broker] sm1/172.16.222.214:48004 (DEFAULT_REGION) CONNECTED
    [broker] * te1/127.0.0.1:48004 (DEFAULT_REGION) CONNECTED

    nuodb [domain] > quit

#### Adding a Transaction Engine (TE)

Adding a vm and starting the broker does not add a TE or a SM.  To add
a TE:

    /opt/nuodb/bin/nuodbmgr --broker localhost --password bird

    NuoDB host version: 2.6.1-5: Community Edition
    nuodb [domain] > start process te host te1:48004 database testdb
    Process command-line options (optional): --dba-user dba --dba-password dba
    Started: [TE] te1/127.0.0.1:48005 (DEFAULT_REGION) [ pid = 4943 ] [ db = testdb ] [ nodeId = 6 ] RUNNING
    nuodb [domain/testdb] >quit

Where `/etc/hosts` has a `172.16.222.140 te1` line in it.

After I added a third vm and added a TE on it I was checked the set up with:

/opt/nuodb/bin/nuodbmgr --broker localhost --password bird

    NuoDB host version: 2.6.1-5: Community Edition
    nuodb [domain] > show domain summary

    Hosts:
    [broker] osboxes/172.16.222.214:48004 (DEFAULT_REGION) CONNECTED
    [broker] te1/172.16.222.140:48004 (DEFAULT_REGION) CONNECTED
    [broker] * te2/127.0.0.1:48004 (DEFAULT_REGION) CONNECTED

    Database: testdb, (unmanaged), processes [2 TE, 1 SM], ACTIVE
    [SM] osboxes/172.16.222.214:48005 (DEFAULT_REGION) [ pid = 4463 ] [ nodeId = 1 ] RUNNING
    [TE] te1/172.16.222.140:48005 (DEFAULT_REGION) [ pid = 6931 ] [ nodeId = 5 ] RUNNING
    [TE] te2/127.0.0.1:48005 (DEFAULT_REGION) [ pid = 4943 ] [ nodeId = 6 ] RUNNING

