# Notes on Hadoop Centos

This sort of follows http://www.server-world.info/en/note?os=CentOS_7&p=hadoop

Date is March 21, 2016.

I am going to use the 3 resource nodes as a cluster with namenode on resource01 and datanodes on
resource02 and 03.

## Creating hadoop user

    Check out my [ansible hadoop](./hadoop/README.md)

## Creating the Data partion and mounting to /mnt/data

The way these machines were set up, I left most of the system unpartioned.

1 of the resource nodes stayed EFI but 2 lost their EFI and are now MSDOS partion drives.

Resource01 is efi.  I put the rest of the drive in /dev/sda5
resource02 and 03 are msdos and so that Docker was all /dev/sda4 I skiped 3 when setting up the docker drive.

Reference: http://ask.xmodulo.com/create-mount-xfs-file-system-linux.html

So I fdisked the rest of the drives into a big partion.

    sudo mkfs.xfs -f /dev/sda3

    (or /dev/sda5)

    sudo mkdir /mnt/data
    sudo mount -t xfs /dev/sda3 /mnt/data

Edit /etc/fstab and add

    /dev/sda3  /mnt/data xfs  defaults  0  0

    (or /dev/sda5)


## Do some configuration by hand

Creation of the hadoop account, key distribution and setting up the software is handled in ansible
scripts in ./hadoop

But some of the configuration seems more straight forward in a tmux session.  So all 3 machines are
being edited at the same time.

### Data Node Directory

    sudo mkdir /mnt/data/datanode
    sudo chown hadoop:wheel /mnt/data/datanode

### Config files

Edit `/opt/hadoop/etc/hadoop/hdfs-site.xml`

    <configuration>
      <property>
        <name>dfs.replication</name>
        <value>2</value>
      </property>
      <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///mnt/data/datanode</value>
      </property>
    </configuration>

Edit `/opt/hadoop/etc/hadoop/core-site.xml`

    <configuration>
      <property>
        <name>fs.defaultFS</name>
        <value>hdfs://resource01:9000/</value>
      </property>
    </configuration>


For java I wantt o lock it to java 1.8.0  so /etc/alternatives/java_sdk_1.8.0 is a good JAVA_HOME

Edit `/opt/hadoop/etc/hadoop/hadoop-env.sh`

Changed export JAVA_HOME to:

    export JAVA_HOME=/etc/alternatives/java_sdk_1.8.0

#### Config changes just for Resource01 The namenode

    sudo mkdir /mnt/data/namenode
    sudo chown hadoop:wheel /mnt/data/namenode

Edit `/opt/hadoop/etc/hadoop/hdfs-site.xml`  add the following to the <configuration> section

    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///mnt/data/namenode</value>
    </property>

Create `/opt/hadoop/etc/hadoop/mapred-site.xml`

    <configuration>
      <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
      </property>
    </configuration>


Edit `/opt/hadoop/etc/hadoop/yarn-site.xml`

    <configuration>
     <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>resource01</value>
      </property>
      <property>
        <name>yarn.nodemanager.hostname</name>
        <value>resource01</value>
      </property>
      <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
      </property>
    </configuration>

Replace `/opt/hadoop/etc/hadoop/slaves` with

    resource01
    resource02
    resource03

### Format Namenode

as hadoop on resource01

    hdfs namenode -format

Note that a lot of output will go by. But it should be all INFO messages.  Check the exit status at the end.
It should be 0

    16/03/22 02:37:34 INFO util.ExitUtil: Exiting with status 0
    16/03/22 02:37:34 INFO namenode.NameNode: SHUTDOWN_MSG:
    /************************************************************
    SHUTDOWN_MSG: Shutting down NameNode at resource01/172.16.222.11
    ************************************************************/


I tried running start-dfs.sh but hadoop doesn't own hadoop home so it could not create the logs directory.

This needs to happen on all 3 machines.

    sudo mkdir logs
    sudo chown hadoop:wheel logs

    start.dfs.sh

returns with:

    Starting namenodes on [resource01]
    resource01: namenode running as process 3579. Stop it first.
    resource01: datanode running as process 3702. Stop it first.
    resource02: starting datanode, logging to /opt/hadoop-2.6.4/logs/hadoop-hadoop-datanode-resource02.out
    resource03: starting datanode, logging to /opt/hadoop-2.6.4/logs/hadoop-hadoop-datanode-resource03.out
    Starting secondary namenodes [0.0.0.0]
    The authenticity of host '0.0.0.0 (0.0.0.0)' can't be established.
    ECDSA key fingerprint is 13:5d:8e:94:e8:42:41:88:19:da:ae:95:2a:d9:0d:37.
    Are you sure you want to continue connecting (yes/no)? yes
    0.0.0.0: Warning: Permanently added '0.0.0.0' (ECDSA) to the list of known hosts.
    0.0.0.0: starting secondarynamenode, logging to /opt/hadoop-2.6.4/logs/hadoop-hadoop-secondarynamenode-resource01.out

I didn't bother getting YARN Up and running.


I did try

    hdfs dfs -mkdir /test
    hdfs dfs -copyFromLocal /opt/hadoop/NOTICE.txt /test
    hdfs dfs -cat /test/NOTICE.txt

