# Notes on installing Mapr

I went ot the main page 

Checked the version of Centos on resource01.  it is 7.2.1511 so it should be 
good for Mapr5.2 per the following matrix. 

    http://maprdocs.mapr.com/home/InteropMatrix/r_os_matrix.html

Download is from here. 

    https://www.mapr.com/products/hadoop-download
    
I checked centos version with 

    cat /etc/centos-release

I had to install wget

    sudo yum install wget
    
Then I got the installer per instructions. 

    $ wget http://package.mapr.com/releases/installer/mapr-setup.sh -P /tmp
    $ sudo bash /tmp/mapr-setup.sh

I accepted the defaults. 

    Enter [host:]port that cluster nodes connect to this host on [resource01:9443]:
    Enter MapR cluster admin user name [mapr]:
    Enter 'mapr' uid [5000]:
    Enter 'mapr' group name [mapr]: 
    Enter 'mapr' gid [5000]: 
    Enter 'mapr' password:    I entered deadmau5
    Confirm 'mapr' password: 
    
It installed for a while and gave this message

    Creating 10 year self signed certificate with subjectDN='CN=*.'
    Certificate stored in file </tmp/tmpfile-maprcert.5750>
    Certificate was added to keystore
    
#### Services

Next step was to install services.  I picked MapR Version 5.2.0  "converged community edition"
using the free license and selected the MEP version 1.1 with the defaults 
of the "MapR Converged Cluster: Batch, Interactive and real-time analytics" 
Auto-Provisioning Template. 

This includes:

 * Async HBase (1.7.0)
 * Drill (1.8)
 * HBase/MapR-DB Common (1.1)
 * Hive(1.2) 
 * Hive Metastore (1.2) 
 * HTTPFS (1.0) 
 * Hue (3.9.0) 
 * Streams Client(0.9.0) 
 * Oozie (4.2.0) 
 * Spark (1.6.1) 
 * YARN + MapReduce (5.2.0)
 
#### Databases

Hive Metastore: 

 * Install MySQL server
 * Username: hive
 * Password: dead*
 * schema: hive
  
Hue:

 * Install MySQL Server
 * Username: hue
 * Password: dead*
 * Schema: hue
 
Oozie: 

 * Install MySQL Server
 * Username: oozie
 * Password: dead*
 * Schema: oozie 
 
#### Monitoring

Metrics 

MapR uses collectd going into OpenTSDB with Grafana UI

 * Install and Set Up Metrics collection infrastructure
 * Install OpenTSDB on a set of nodes in the cluster
 * Install Grafana on one node in the cluster

Logs

 MapR uses Fluentd with Elastic Search and Kibana
 
 * Install and set up log collection infrastructure
 * Install Elasticsearch on a set of nodes
    * Index Directory: /opt/mapr/es_db
    
#### Cluster

MapR Adminstrator Account

 * Username: mapr
 * admin group: mapr
 * password: dead
 * UID: 5000
 * GID: 5000
 * Cluster Name: my.cluster.com
 
#### Configure Nodes 

This is where they ask to configure disks and want to format my drives, 
partitions.  These disks are not defined on a per node basis so there is
an assumption of similarity.  If a node doesn't have a certain drive 
then it gives a warning.

Also configure Remote Authentication.   ssh password or private key

