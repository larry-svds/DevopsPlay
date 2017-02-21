# Minio on dcos

This one was braindead simple.  Started it from universe and it showed up
on the marathon-lb.  

I did have to check the service to see which port it took.

For my own notes `http://172.16.222.8:10108/`


## Using the Python Client

Docs for [Minio Python library for Amazon S3 Compatible Cloud Storage](https://docs.minio.io/docs/python-client-quickstart-guide)
are clear enough. 

ONE NOTE: You'll need the `Access Key` and `Secret Key`

These are in the logs of the instance of the service. 

In the DC\OS Interface http://172.16.222.7

Go to services, pick minio, go to an instance.  click on the log tab and 
it should be right at the begining of the log. 

    from minio import Minio
    from minio.error import ResponseError
    mc = Minio('172.16.222.8:10108',"<ACCESS KEY>",
        "<secret key>", secure=False)

Obviously the stuff between `<>` is replaced with the values from the logs. 
If you say secure=True, then you will need to set up SSL.  #TODO Set up SSL

    # Make a bucket with the make_bucket API call.
    try:
           minioClient.make_bucket("maylogs", location="us-east-1")
           
Interestingly, minio does pretend to be `us-east-1` but you can leave 
off the location and this still works.
           
    except ResponseError as err:
           print(err)
    else:
            # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.
            try:
                   minioClient.fput_object('maylogs', 'pumaserver_debug.log', '/tmp/pumaserver_debug.log')

You can also do `bob/bob/pumaserver_debug.log` and it will create the directories 
in the bucket.

            except ResponseError as error:
                   print(error)  
                       
## Reading S3 into dataframes on Spark Workers

Spark provided in DC/OS is Spark 2.0 with Hadoop 2.6 libraries. 

TO get to S3 Spark uses Hadoop libraries.  Some of which have issues with S3.. 

S3 comes in 3 flavors. `s3//` deprecated, `s3n//` better, now unmaintained, for hadoop < 2.7, and `s3a//` for 
hadoop 2.7 + without size limits. 

But first you have to register your S3 within the hadoop configs. 

here is the scala code we need to emulate. Note that in the [this databricks issue](https://github.com/databricks/spark-csv/issues/137)
the person says this works, after he added some jars. Would have been nice to 
know which ones.. So I converted that to pyspark.
    
    sc= spark.sparkContext 
    hadoopConf = sc._jsc.hadoopConfiguration()
    
    hadoopConf.set("fs.s3n.endpoint", "172.16.222.8:10108")
    hadoopConf.set("fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem")
    hadoopConf.set("fs.s3n.awsAccessKeyId","3PAO<and stuff>LEZ0")
    hadoopConf.set("fs.s3n.awsSecretAccessKey","mtwv1QsvoL<and stuff>KNsXWbHLP")
    s3path ="s3n://bucketthing/hosts"
    df = sc.textFile(s3path)
    df.first() 
    java.lang.RuntimeException: java.lang.ClassNotFoundException: Class org.apache.hadoop.fs.s3native.NativeS3FileSystem not found

[This Stack Overflow (and many others)](http://stackoverflow.com/questions/28029134/how-can-i-access-s3-s3n-from-a-local-hadoop-2-6-installation)
identifies this as hadoop-aws-[version].jar not being in the 2.6 
classpath.  They also say.. it needs to get in `export HADOOP_CLASSPATH`

The [hadoop-aws-2.6.0.jar](https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/2.6.0) can be downloaded. 

From within the mesosphere spark driver docker container. 

    curl -O http://central.maven.org/maven2/org/apache/hadoop/hadoop-aws/2.6.0/hadoop-aws-2.6.0.jar
    
I then had to put it at /root for it to find it with the --jar directive. 

    root@resource01:/opt/spark/dist# ./bin/pyspark --master mesos://172.16.222.7:5050 
    --conf spark.mesos.executor.docker.image=mesosphere/spark:1.0.4-2.0.1 
    --conf spark.mesos.executor.home=/opt/spark/dist --jars hadoop-aws-2.6.0.jar
    
When I ran it again.. this time I get:

    Caused by: java.lang.ClassNotFoundException: com.amazonaws.AmazonServiceException

I tried: 
    
    curl -O http://central.maven.org/maven2/com/amazonaws/aws-java-sdk-s3/1.11.91/aws-java-sdk-s3-1.11.91.jar
    curl -O http://central.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.11.91/aws-java-sdk-core-1.11.91.jar

added it to jars

    --jars hadoop-aws-2.6.0.jar,aws-java-sdk-s3-1.11.91.jar,aws-java-sdk-core-1.11.91.jar
    
and woo hoo.
    
    py4j.protocol.Py4JJavaError: An error occurred while calling o26.partitions.
    : org.apache.hadoop.security.AccessControlException: Permission denied: s3n://bucketthing/hosts
    
So jars fixed.. now where do I set the location of the S3 repo?

https://github.com/minio/minio/issues/2965   
    
So I added:

    hadoopConf.set("fs.s3n.endpoint", "172.16.222.8:10108")

And got his.. 
    
    py4j.protocol.Py4JJavaError: An error occurred while calling o26.partitions.
    : org.apache.hadoop.security.AccessControlException: Permission denied: s3n://bucketthing/hosts    

At this point I stoped and and read through the [minio github issue 2965](https://github.com/minio/minio/issues/2965)
    
THis issue with a specific reference to minio usage.. like many other things, identifies 2,6 as a problem and he 
worked out his solution on 2.7.  

Looking at the spark running in dc/os it is docker container `mesosphere/spark` tag `1.0.7-2.1.0-hadoop-2.6` but they also 
out put tag `1.0.7-2.1.0-hadoop-2.7` at the same time. 

So combine minio github issue 2965 and switching to hadoop-2.7

##### Setting Hadoop Configs in your PySpark Script. 

This is a bit hacky.. (`_jsc`) but is nicer than the pass a dictionary way
offered to spark python users. [Reference](http://stackoverflow.com/questions/28844631/how-to-set-hadoop-configuration-values-from-pyspark)

    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set('fs.s3n.awsAccessKeyId',
    
here is the scala code we need to emulate. 
    
    scala> val hadoopConf = sc.hadoopConfiguration
    scala> hadoopConf.set("fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem")
    scala> hadoopConf.set("fs.s3n.awsAccessKeyId", "****")
    scala> hadoopConf.set("fs.s3n.awsSecretAccessKey", "****")
    
    scala> val s3path = "s3n://bucket/sample.csv"
    scala> val df = sc.textFile(s3path)
    scala> df.first()
    java.lang.RuntimeException: java.lang.ClassNotFoundException: Class org.apache.hadoop.fs.s3native.NativeS3FileSystem not found
 
 
in PySpark 2.0 this looks like 
  
    sc= spark.sparkContext 
    hadoopConf = sc._jsc.hadoopConfiguration()
    
    hadoopConf.set("fs.s3n.endpoint", "172.16.222.8:10108")
    hadoopConf.set("fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem")
    hadoopConf.set("fs.s3n.awsAccessKeyId","3PAONS7Y5ZZRUIIRLEZ0")
    hadoopConf.set("fs.s3n.awsSecretAccessKey","mtwv1QsvoL+o2IUWbs0wYL44Pevf5dFKNsXWbHLP")
    s3path ="s3n://bucketthing/hosts"
    df = sc.textFile(s3path)
    df.first() 
    
