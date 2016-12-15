# Notes on Hadoop OSX

These notes are for March 20, 2016

All the notes seem to be about making a standalone or psuedo-distributed hadoop. Which is
totally understandable but I want to make a distributed one.

You can do this from homebrew or downloading the files directly.   Downloading the files
directly seems to be more likely to lead me to the info I need to make it fully distrubuted.

Least Magic by not using homebrew.

Using Homebrew:

https://getblueshift.com/setting-up-hadoop-2-4-and-pig-0-12-on-osx-locally/
http://boatboat001.com/index.php/blogs/view/setting_up_a_hadoop_cluster_under_mac_os_x_mountain

But without homebrew:

http://zhongyaonan.com/hadoop-tutorial/setting-up-hadoop-2-6-on-mac-osx-yosemite.html

1. added Java 8 from http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html
2. Created a hadoop user on the mac using the settings tool.  I made it a sudoer as well.
3. logged into hadoop
4. Created clean keys.  I went ahead and used DSA as they suggest on the hadoop site. I have seen
that rsa will work just as well.

    $ ssh-keygen -t dsa -P '' -f ~/.ssh/id_dsa
    $ cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys

tested with

    ssh localhost

and

    ssh pick

where pick is my hostname.  turned out I needed to update my /etc/host file with the hosts in my network.

5. Download a hadoop distro.

http://www.apache.org/dyn/closer.cgi/hadoop/common/

I grabed the most recent stable release.  hadoop-2.7.2


I grabbed

    curl http://apache.mirrors.pair.com/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz -ls

Unpacked it in the base /Users/hadoop directory

    gunzip hadoop-2.7.2.tar.gz
    tar xvf hadoop-2.7.2.tar


    export JAVA_HOME=`/usr/libexec/java_home`

    export HADOOP_PREFIX="/Users/hadoop/hadoop-2.7.2"


Then I put both these into a .bash_profile that I had to create.

For a discussion of why it ends up being .bash_profile

    http://www.joshstaiger.org/archives/2005/07/bash_profile_vs.html

While we are at it, here is an interesting discussion of stuff to put in .bash_profile

    https://natelandau.com/my-mac-osx-bash_profile/

Next go to the hadoop root etc directory

    cd ${HADOOP_PREFIX}/etc/hadoop

Edit following config files in your Hadoop directory.  Note compared to the source blog I added directory
location.

 * etc/hadoop/core-site.xml:

        <configuration>
            <property>
                <name>fs.defaultFS</name>
                <value>hdfs://localhost:9000</value>
            </property>
        </configuration>

 * etc/hadoop/hdfs-site.xml:

        <configuration>
            <property>
                <name>dfs.replication</name>
                <value>1</value>
            </property>
            <property>
                <name>dfs.name.dir</name>
                <value>/Users/hadoop/dfs/name</value>
            </property>
            <property>
                <name>dfs.data.dir</name>
                <value>/Users/hadoop/dfs/data</value>
            </property>
        </configuration>

 * etc/hadoop/mapred-site.xml:

        <configuration>
            <property>
                <name>mapreduce.framework.name</name>
                <value>yarn</value>
            </property>
        </configuration>

 * etc/hadoop/yarn-site.xml:

        <configuration>
            <property>
                <name>yarn.nodemanager.aux-services</name>
                <value>mapreduce_shuffle</value>
            </property>
        </configuration>


in the $HADOOP_PREFIX directory initialize the name node with:

    bin/hdfs namenode -format

A lot of output goes buy and it endes with SHUTDOWN_MSG.  look it over. This can be totally file. The output is
INFO messages.  Check for ERRORS and if not.. Start hdfs up with:

    sbin/start-dfs.sh

Which will output something like.

    16/03/20 20:24:09 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Starting namenodes on [localhost]
    localhost: starting namenode, logging to /Users/hadoop/hadoop-2.7.2/logs/hadoop-hadoop-namenode-Pick.local.out
    localhost: starting datanode, logging to /Users/hadoop/hadoop-2.7.2/logs/hadoop-hadoop-datanode-Pick.local.out
    Starting secondary namenodes [0.0.0.0]
    The authenticity of host '0.0.0.0 (0.0.0.0)' can't be established.
    ECDSA key fingerprint is SHA256:HvuyK27I5R8zjvMxHnoowiZqc8FrJb+peSVGqcMfoKg.
    Are you sure you want to continue connecting (yes/no)?

I said yes. This question might not happen to you if you have logged into this IP before.

    0.0.0.0: Warning: Permanently added '0.0.0.0' (ECDSA) to the list of known hosts.
    0.0.0.0: starting secondarynamenode, logging to /Users/hadoop/hadoop-2.7.2/logs/hadoop-hadoop-secondarynamenode-Pick.local.out
    16/03/20 20:24:30 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable

This is just a warning but if you want to know more about it: https://hadoop.apache.org/docs/r2.7.1/hadoop-project-dist/hadoop-common/NativeLibraries.html

You can browse to hdfs page at port 50070 ie. http://pick:50070 on a machine named pick.  localhost works too if you
are on the machine that you are adding hadoop too.

Make a directory to put stuffs

    bin/hdfs dfs -mkdir /user
    bin/hdfs dfs -mkdir /user/hadoop

You'll probably get teh annoying native-libraries comment for every commmand.

Start up yarn with:

    sbin/start-yarn.sh

This is less chatty.  Not though that logs are not going to /var/log.

See the interface at `http://localhost:8088`

Copy some files:

    bin/hdfs dfs -put etc/hadoop input

Run a program.

    bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.2.jar grep input output 'dfs[a-z.]+'


This failed so I need to figure that out but I need to move on to sparky stuff
