# Installing Confluent Open Source Kafka on Centos 7

I am using Confluent vs Apache because of the additions included.

This is going to be a single instance kafka.

From http://docs.confluent.io/3.2.0/installation.html#rpm-packages-via-yum


    ssh centos@control01

    sudo rpm --import http://packages.confluent.io/rpm/3.2/archive.key

    sudo vi /etc/yum.repo.d/confluent.repo

With content:

    [Confluent.dist]
    name=Confluent repository (dist)
    baseurl=http://packages.confluent.io/rpm/3.2/7
    gpgcheck=1
    gpgkey=http://packages.confluent.io/rpm/3.2/archive.key
    enabled=1

    [Confluent]
    name=Confluent repository
    baseurl=http://packages.confluent.io/rpm/3.2
    gpgcheck=1
    gpgkey=http://packages.confluent.io/rpm/3.2/archive.key
    enabled=1


then

    sudo yum clean all
    sudo yum install confluent-platform-oss-2.11


