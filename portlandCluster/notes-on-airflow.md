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

Was able to do this pretty much as [shown here](https://kyungw00k.github.io/2016/05/04/setup-airflow/)
I  did not do the python install as I already have anaconda3. I had 
airflow as well, but pip install airflow changed my flask back to 0.10 from 0.12. I also 
added the export to .bash_profile. 

On my machine that already has Anaconda3 and brew

    pip install airflow
    mkdir ~/airflow

Add `export AIRFLOW_HOME=~/airflow` to .bash_profile

    cd ~/airflow && airflow initdb
    airflow webserver -p 8080

## Airflow tutorial

From the start I want to modify the tutorial to do the things I am trying to do.

The basic idea is that an executor dag has to download the git for the model as well as secure a
execution cluster.  Then it needs to run the script. To do this the dag has to look like..

    GetGit >> RunIt << GetCluster
    
Both GetGit and GetCluster can run in parallel, RunIt is dependant on those two finishing first. 


##### Setting up Intellij to see Airflow

Set the Project SDK to the correct python.  In my case the anaconda python 3 install I did.
  
##### Default Args

First section of the tutorial lists a bunch of default_args.  

> default_args (dict) – A dictionary of default parameters to be used as constructor keyword parameters 
when initialising operators. Note that operators have the same hook, and precede those defined here,
meaning that if your dict contains ‘depends_on_past’: True here and ‘depends_on_past’: False in the 
operator’s call default_args, the actual value will be False.

A good discussion of most of the things you set for this is found in the 
[documentaiton on BaseOperator](https://airflow.incubator.apache.org/code.html#baseoperator)

##### Owner

Owner is a bit complicated.. I did some searching and it is not clear to me how this is used.  I am going to
set it to centos and see if it causes any problems.  Centos is the user running on my airflow install now.
I'll have to get airflow user running if this is an issue.  User larry is running it on my mac. # todo: 
 
###### Dates

This is a complex set of things. 

 * `start_date` is the first date that should have run.  This allows for back
filling data, which is often a part of any new pipeline or pipleline change.  
 * `depends_on_past` when set to true 
requires that previous runs should have happened.  
 * `end_date` stops the scheduler from marching on.  If left
blank then it is open ended.  This can be handy for patching data sets. 
 * `wait_for_downstream` if true then `depends_on_past` is set true, but I am not clear on how
it does more than that.  It is a stronger condition somehow.  # todo wait_for_downstream vs depends_on_past

###### Email

You can set several things about email.  Which begs the question.. how does airflow send email?

Answer is in `~/airflow/airflow.cfg`

    [email]
    email_backend = airflow.utils.email.send_email_smtp
    
    [smtp]
    # If you want airflow to send emails on retries, failure, and you want to use
    # the airflow.utils.email.send_email_smtp function, you have to configure an smtp
    # server here
    smtp_host = localhost
    smtp_starttls = True
    smtp_ssl = False
    smtp_user = airflow
    smtp_port = 25
    smtp_password = airflow
    smtp_mail_from = airflow@airflow.com

// now # TODO set up email on control01.  

