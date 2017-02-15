# Notes on Airflow

Settting up Airflow to handle workflow for a Data Science Model Management application. 

## Install Airflow on Centos 7.3 (1611)

Going to install it on my Nuc Cluster on Control01.  This is next to my DC/Cluster and I am 
going to use DC/OS as the executor cluster for Airflow. 

## [Quick Start](https://airflow.incubator.apache.org/start.html)

I need to install pip on this fresh centos box. 

First you need to [add epel](https://www.cyberciti.biz/faq/installing-rhel-epel-repo-on-centos-redhat-7-x/)

    sudo yum install epel-release
    
Then pip. 

    sudo yum install -y python-pip
    sudo pip install --upgrade pip
    sudo pip uninstall setuptools
    sudo pip install setuptools

Errors in `pip install airflow` led me to these prereqs     
    
    sudo yum install python-devel
    sudo yum install gcc
    
followed by airflow.. quickstart version.



    sudo pip install airflow

and to get rid of an error in the airflow initdb..

    sudo pip install airflow[hive]
    airflow initdb
    
And to allow the webserver to run when the client is not plugged in.. in this quick start config. 

    sudo yum install -y screen 
    
    screen
    airflow webserver -p 8080 
    
## Install Airflow on Mac Sierra