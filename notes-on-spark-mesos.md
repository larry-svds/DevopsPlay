# Notes on Spark on Mesos


Working through: http://spark.apache.org/docs/latest/running-on-mesos.html

I installed spark without hadoop on all the slaves. See `spark/README.md` in the spark directory
where I used a ansible role to install it on my workers.

you also need the mesos library local to the submitter.  I brewp install mesos to get that.

    export MESOS_NATIVE_JAVA_LIBRARY=/usr/local/Cellar/mesos/0.28.0/lib/libmesos.dylib

The thing about this is that if you install spark on the workers you ahve to make it clear where the
spark is.   This is `spark.mesos.executor.home` which defaults to `SPARK_HOME`.

    ./spark-shell -c spark.executor.home=/opt/spark --master mesos://zk://control01:2181/mesos

Then fixing the authentication problem..

    ./bin/spark-shell -c spark.executor.home=/opt/spark --master mesos://zk://mesos:Ed6Kla4V7dpvwF50@control01:2181/mesos \
     -c spark.mesos.principal=spark -c spark.mesos.secret=mysecret

And then the problem with snappy http://apache-spark-user-list.1001560.n3.nabble.com/How-to-avoid-use-snappy-compression-when-saveAsSequenceFile-td17350.html

As well as switching it to spark-submit

    /opt/spark/bin/spark-submit -c spark.executor.home=/opt/spark --master mesos://zk://mesos:Ed6Kla4V7dpvwF50@control01:2181/mesos \
     -c spark.mesos.principal=spark -c spark.mesos.secret=mysecret \
     -c spark.io.compression.codec=org.apache.spark.io.LZ4CompressionCodec \
     --class com.svds.hashtag.Battle hashtag-battle-assembly-1.0.jar --hashtags love,twitter --output-stdout > output

## Talking to HDFS 

Installed hadoop on resource01-03 with a namenode on 01 and datanodes on 02 and 03. 

From your spark context... 

    val textFile = sc.textFile("hdfs://resource01:9000/test/NOTICE.txt")
    textFile.first()
    
should print a line of text assuming that on if you loggeed into hadoop on one of the resource nodes 
and typed: 

    hdfs dfs -cat /text/NOTICE.txt
    
shows the contents of an existing file.
 
 ## Setting up Spark 1.6 on my laptop in Oct 2016.
 
 The version of Mesos now is 1.0.1.. so the 0.28.0 

## Getting spark-shell to work from my mac
 
You have to log into hadoop user or centos user.. for some reason the spark app 
will want to run as your user name on the back end system.  

When I tried to run it as larry the app tasks failed with 
"Failed to change user to 'larry': Failed to getgid: unknown user".  I found 
this by looking at the output of the failed task in the mesos interface.   You need to 
look at the mesos interface relatively quickly as the spark framework, or mesos, 
cleans up spark app task logs and it doesn't show in the mesos UI any more. 

SO I created a hadoop user and it all worked.. serveral key points. 

THe call, from the /opt/spark directory is 

    ./bin/spark-shell -c spark.executor.home=/opt/spark \
    --master mesos://zk://mesos:Ed6Kla4V7dpvwF50@control01:2181/mesos \
    -c spark.mesos.principal=spark \
    -c spark.mesos.secret=mysecret \
    -c spark.io.compression.codec=org.apache.spark.io.LZ4CompressionCodec 

If you don't put the LZ4 you get an error about Snappy compression. 

You also have to have
 
    export MESOS_NATIVE_JAVA_LIBRARY=/usr/local/Cellar/mesos/1.0.1/lib/libmesos.dylib
    
working in the shell wehre you are logged into hadoop.   Notice that 
this says 1.0.1.  That is becasue when I installed mesos on my machine in 
Oct 2016 that was the version that gets installed. 

It seems to work fine against a cluster running mesos 0.28.0. 

Running pyspark is the same.. 

    ./bin/pyspark -c spark.executor.home=/opt/spark \
    --master mesos://zk://mesos:Ed6Kla4V7dpvwF50@control01:2181/mesos \
    -c spark.mesos.principal=spark \
    -c spark.mesos.secret=mysecret \
    -c spark.io.compression.codec=org.apache.spark.io.LZ4CompressionCodec 
