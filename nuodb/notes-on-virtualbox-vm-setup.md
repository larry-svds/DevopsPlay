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
    alternatives --config

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

    # sudo rpm -i nuodb-ce-2.6.1.5.x86_64.rpm
    NOTE: The NuoDB Broker is not configured.

    Please set a domain password in /opt/nuodb/etc/default.properties,
    then run 'service nuoagent start' to bring up the Broker.


