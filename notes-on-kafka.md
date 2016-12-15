#notes on Kafka

I'll go ahead and use http://itekblog.com/kafka-centos-installation-instructions/
as a starting point.

Some problems I wil have to deal with is I want to put these on hosts that already have kafka.

    sudo yum install wget

We currently are on kafka 0.8 at work so I am going ot go ahead and use that.  The main kafka
page also recommended using the scala 2.10 binaries.  Note that this is only important if you are
programmming in scala.

I went to the download page and picked the most recent 8.2 on scala 2-10. http://kafka.apache.org/downloads.html

    sudo wget http://apache.osuosl.org/kafka/0.8.2.2/kafka_2.10-0.8.2.2.tgz

    sudo tar xvf kafka_2.10-0.8.2.2.tgz
    ln -s kafka_2.10-0.8.2.2 kafka

Now I have a /opt/kafka directory where I will set any KAFKA_HOME type things.


## Dealing with Zookeeper

I already have zookeeper and it is used for Mesos And Marathon.

I looked at the `bin/kafka/-server-start.sh` and its quite short. Seems to be a -daemon mode which I should use.
and then mostly it loads a server.properties file.

From the page(and the official quick start)  this is  `config/server.properties`

I looked at `/opt/kafka/config/server.properties` and at the end there is the following.

    ############################# Zookeeper #############################

    # Zookeeper connection string (see zookeeper docs for details).
    # This is a comma separated host:port pairs, each corresponding to a zk
    # server. e.g. "127.0.0.1:3000,127.0.0.1:3001,127.0.0.1:3002".
    # You can also append an optional chroot string to the urls to specify the
    # root directory for all kafka znodes.
    zookeeper.connect=localhost:2181

    # Timeout in ms for connecting to zookeeper
    zookeeper.connection.timeout.ms=6000

I changed the connect line to

    zookeeper.connect=control01:2181,control02:2181,control03:2181/kafka

The fact that you only put the chroot at the end of everything is sonething I discovered by looking for examples
online.   The other option is you put the chroot per host.

Now run the server

    sudo ./bin/kafka-server-start.sh config/server.properties

A good amount of output comes out and then it slows down to a stop at:

    [2016-03-21 07:26:45,297] INFO 0 successfully elected as leader (kafka.server.ZookeeperLeaderElector)
    [2016-03-21 07:26:45,364] INFO Registered broker 0 at path /brokers/ids/0 with address control01:9092. (kafka.utils.ZkUtils$)
    [2016-03-21 07:26:45,373] INFO [Kafka Server 0], started (kafka.server.KafkaServer)
    [2016-03-21 07:26:45,409] INFO New leader is 0 (kafka.server.ZookeeperLeaderElector$LeaderChangeListener)

Then open another window on control01

We are now at the point of creating a topic and again there is the --zookeper parameter for bin/kafka-topics.sh
and so I need to investigate and see what I need to do with a full cluster and chroot.

This script basically calls `kafka-run-class.sh`. This goes down and seems to run the kafka without interpreting
this. So I feel safe  replacing --zookeeper with --zookeeper.connect.  This errored with unrecognized option, but:

    bin/kafka-topics.sh --create --zookeeper "control01:2181,control02:2181,control03:2181/kafka" --replication-factor 1 --partitions 1 --topic test

Came back with 'Created topic "test"'

I then could run

    ./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test

Which waited for input.  So I typed a few lines.

In another window run

    ./bin/kafka-console-consumer.sh --zookeeper control01:2181,control02:2181,control03:2181/kafka --topic test --from-beginning

and it shows the lines you entered in the producer, infact if left on it now echos whatever you type in the producer.

