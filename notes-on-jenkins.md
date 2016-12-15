

All this happened on the jenkins master sandbox stderr without any jenkins framework being live on mesos master
and no new tasks appeared.  

    INFO: SCM changes detected in buildci. Triggering  #47
    Jan 7, 2016 6:11:19 AM org.jenkinsci.plugins.mesos.MesosCloud provision
    INFO: Provisioning Jenkins Slave on Mesos with 1 executors. Remaining excess workload: 0 executors)
    Jan 7, 2016 6:11:19 AM hudson.slaves.NodeProvisioner$StandardStrategyImpl apply
    INFO: Started provisioning MesosCloud from MesosCloud with 1 executors. Remaining excess workload: 0
    Jan 7, 2016 6:11:19 AM org.jenkinsci.plugins.mesos.MesosComputerLauncher <init>
    INFO: Constructing MesosComputerLauncher
    Jan 7, 2016 6:11:19 AM org.jenkinsci.plugins.mesos.MesosSlave <init>
    INFO: Constructing Mesos slave mesos-jenkins-5de6ac55-2943-4c09-b19f-782bf5330889 from cloud
    Jan 7, 2016 6:11:20 AM hudson.model.AsyncPeriodicWork$1 run
    INFO: Started Mesos pending deletion slave cleanup
    Jan 7, 2016 6:11:20 AM hudson.model.AsyncPeriodicWork$1 run
    INFO: Finished Mesos pending deletion slave cleanup. 3 ms
    Jan 7, 2016 6:11:29 AM org.jenkinsci.plugins.mesos.MesosComputerLauncher launch
    INFO: Launching slave computer mesos-jenkins-5de6ac55-2943-4c09-b19f-782bf5330889
    Jan 7, 2016 6:11:29 AM org.jenkinsci.plugins.mesos.MesosComputerLauncher launch
    INFO: Sending a request to start jenkins slave mesos-jenkins-5de6ac55-2943-4c09-b19f-782bf5330889
    Jan 7, 2016 6:11:29 AM org.jenkinsci.plugins.mesos.JenkinsScheduler requestJenkinsSlave
    INFO: Enqueuing jenkins slave request
    Jan 7, 2016 6:11:30 AM hudson.slaves.NodeProvisioner update
    INFO: MesosCloud provisioning successfully completed. We have now 2 computer(s)
    Jan 7, 2016 6:12:01 AM hudson.triggers.SCMTrigger$Runner run
    INFO: SCM changes detected in buildci. Triggering  #47
    Jan 7, 2016 6:12:20 AM hudson.model.AsyncPeriodicWork$1 run
    INFO: Started Mesos pending deletion slave cleanup
    Jan 7, 2016 6:12:20 AM hudson.model.AsyncPeriodicWork$1 run
    INFO: Finished Mesos pending deletion slave cleanup. 2 ms
    Jan 7, 2016 6:13:01 AM hudson.triggers.SCMTrigger$Runner run
    INFO: SCM changes detected in buildci. Triggering  #47

In the Jenkins configuration there is a cloud config.  The port has to be 15050 for mesos to get around the proxy.

You also have to create a secret which turns out to be anything that you put in the mesos configuration
and the framework configuration.

principal and secret in Jenkins is available on the jenkins configuration page.

for the mesos side.  

  



Turns off auth in /etc/default/nginx-mesos-leader.env  this is loaded into the  nginx-consul container in
nginx-mesos-leader.service

    NGINX_KV=service/nginx/templates/mesos-leader
    NGINX_AUTH_TYPE=basic
    NGINX_AUTH_BASIC_KV=service/nginx/auth/users
    NGINX_PUBLIC_IP=172.16.222.8
    CONSUL_CONNECT=consul.service.consul:8500
    CONSUL_SSL=true
    CONSUL_LOGLEVEL=info


set basic to nothing.
also set NGINX_AUTH_BASIC_KV to nothing.  

    NGINX_AUTH_TYPE=
    NGINX_AUTH_BASIC_KV=


Also turned off authentication in  `/etc/default/mesos-master`

    PORT=15050
    ZK=`cat /etc/mesos/zk`
    CLUSTER=cluster1
    MESOS_QUORUM=2
    export MESOS_IP=172.16.222.8
    export MESOS_HOSTNAME=control03.node.consul
    export MESOS_AUTHENTICATORS=crammd5
    export MESOS_AUTHENTICATE=true
    export MESOS_AUTHENTICATE_SLAVES=true
    export MESOS_CREDENTIALS=/etc/mesos/credentials


    export MESOS_AUTHENTICATE=false
    export MESOS_AUTHENTICATE_SLAVES=false


also turned off.. `/etc/mesos-leader.nginx`


    location / {
            proxy_connect_timeout   600;
            proxy_send_timeout      600;
            proxy_read_timeout      600;
            send_timeout            600;

            auth_basic              on;
            auth_basic_user_file    /etc/nginx/nginx-auth.conf;

            proxy_pass http://{{ env "NGINX_PUBLIC_IP" }}:15050/;
    }

became

            auth_basic              off;


Still no cigar.   I think mesos might be fine but jenkins is not.

The Marathon call is

    java -Djava.library.path=/usr/local/lib:/usr/lib:/usr/lib64
         -Djava.util.logging.SimpleFormatter.format=%2$s%5$s%6$s%n
         -Xmx512m
         -cp /usr/bin/marathon
         mesosphere.marathon.Main
         --mesos_authentication_principal marathon
         --mesos_authentication_secret_file /etc/marathon/mesos_authentication_secret
         --zk zk://marathon:DxM9xNoY78Rp9sMU@zookeeper.service.consul:2181/marathon
         --http_port 18080
         --event_subscriber http_callback
         --hostname control01.node.consul
         --artifact_store file:///etc/marathon/store
         --logging_level warn
         --master zk://mesos:ajbM8GNV7sf7UV7t@zookeeper.service.consul:2181/mesos
