# Notes on ODG Fast Score

## First with docker compose on my mac.

You need docker and docker-compose.  type `docker-compose` and see if
you get help. They were for me so not going into that.

I am following [the fast score installation page](http://docs.opendatagroup.com/docs/getting-started-with-fastscore#installing-fastscore)

I put software systems that i am just playing with in  the `~/software`
directory.

    cd ~/software
    mkdir fastscore
    cd fastscore

Next create a database docker volume. As well as the `docker-compose.yml`

    docker volume create --name=db
    vi docker-compose.yml

and fill it with this from the instructions.


    version: '2'
    services:
      dashboard:
        image: fastscore/dashboard:1.3
        network_mode: "host"
        stdin_open: true
        tty: true
        environment:
          CONNECT_PREFIX: https://127.0.0.1:8001

      connect:
        image: fastscore/connect:1.3
        network_mode: "host"
        stdin_open: true
        tty: true

      engine-1:
        image: fastscore/engine-x:1.3
        network_mode: "host"
        stdin_open: true
        tty: true
        environment:
            CONNECT_PREFIX: https://127.0.0.1:8001

      database:
        image: fastscore/model-manage-mysql:1.3
        network_mode: "host"
        volumes:
          - db:/var/lib/mysql

      model-manage:
        image: fastscore/model-manage:1.3
        network_mode: "host"
        stdin_open: true
        tty: true
        depends_on:
          - connect
          - database
        environment:
          CONNECT_PREFIX: https://127.0.0.1:8001

    volumes:
      db:
        external: true


With that in place.

    docker-compose up -d

check that it is up

    docker ps
    CONTAINER ID        IMAGE                              COMMAND                  CREATED             STATUS              PORTS               NAMES
    37461fc1e3f7        fastscore/model-manage:1.3         "/bin/sh -c bin/mo..."   11 minutes ago      Up 11 minutes                           fastscore_model-manage_1
    f0ffcbced4c6        fastscore/engine-x:1.3             "/bin/sh -c bin/en..."   11 minutes ago      Up 11 minutes                           fastscore_engine-1_1
    5fd431332301        fastscore/connect:1.3              "/bin/sh -c bin/co..."   11 minutes ago      Up 11 minutes                           fastscore_connect_1
    f4d76b4e20ac        fastscore/model-manage-mysql:1.3   "/bin/sh -c '/sbin..."   11 minutes ago      Up 11 minutes                           fastscore_database_1
    635752861ab6        fastscore/dashboard:1.3            "npm run start-fds"      11 minutes ago      Up 11 minutes                           fastscore_dashboard_1

##### Set up CLI

You need python 2 to run this environment.  I have anaconda3 installed.. as
well as brew python2.  `/usr/local/bin/python` is brew's 2.7.13 so.

    virtualenv -p /usr/local/bin/python venv
    source venv/bin/activate

You will need to be in a python2 environment whenever you run the
cli commands.

    wget https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.3.tar.gz
    tar xzf fastscore-cli-1.3.tar.gz
    cd fastscore-cli-1.3
    sudo python setup.py install

##### Configure the cluster

Next you want to create `config.yml` with the following content:

    fastscore:
      fleet:
        - api: model-manage
          host: localhost
          port: 8002
        - api: engine-x
          host: localhost
          port: 8003

      db:
        type: mysql
        host: localhost
        port: 3306
        username: root
        password: root

      pneumo:
        type: kafka
        bootstrap:
          - localhost:9092
        topic: notify

Then push that config to fastscore.

AND BOOM

Host networking doesn't work on `docker for mac`.

## ODG On Ubuntu 16.04

Team uses Ubuntu so use that.  A quick attempt with Centos 7 didn't work with host networking
proably due to iptables, so moving into the Ubuntu world of carefree living.

Downloaded ubuntu 16.04 from [osboxes.org ubuntu page](http://www.osboxes.org/ubuntu/)

Set up a virtual machine with 3 cpu and 8 gigs of ram.
To keep it super simple.. (since all I really need is the ports so I can
configure this for DC/OS)

    sudo apt-get update

Is always the thing you do in ubuntu.

Default python is python 2.7.11.. yay. Pip is not.
Note on the fail is to run. `sudo apt-get install python-pip`

Then do this page for [docker for ubuntu](https://docs.docker.com/engine/installation/linux/ubuntu/)

You wont need to do the part they recommend for 14.04.

Next do docker compose with `sudo apt-get install docker-compose`

Oops if you do this when you run against their Compose script you will get a
cryptic error aobut `service 'version' doesnt have any configuration options.`
This just means that your version of docker-compose is not the right one.

[Here is the official page.](https://github.com/docker/compose/releases)

So:
    sudo apt-get remove docker-compose

if you installed it with apt-get and then do the steps on the link above.


Next, You then create the db volume, since the docker compose script
refers to it.

    sudo docker volume create --name=db

and then create the docker-compose.yml as in the mac section above,
followed by `sudo docker-compose up -d`.  Once it is running you should
see the following services listening.

    osboxes@osboxes:~/odg$ netstat -atp tcp
    (Not all processes could be identified, non-owned process info
     will not be shown, you would have to be root to see it all.)
    Active Internet connections (servers and established)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 osboxes:domain          *:*                     LISTEN      -
    tcp        0      0 *:8001                  *:*                     LISTEN      -
    tcp        0      0 *:8002                  *:*                     LISTEN      -
    tcp        0      0 *:8003                  *:*                     LISTEN      -
    tcp6       0      0 [::]:8000               [::]:*                  LISTEN      -
    tcp6       0      0 [::]:mysql              [::]:*                  LISTEN      -
    osboxes@osboxes:~/odg$ sudo lsof -i -P
    [sudo] password for osboxes:
    COMMAND     PID       USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
    avahi-dae   589      avahi   12u  IPv4  12040      0t0  UDP *:5353
    avahi-dae   589      avahi   13u  IPv6  12041      0t0  UDP *:5353
    avahi-dae   589      avahi   14u  IPv4  12042      0t0  UDP *:39273
    avahi-dae   589      avahi   15u  IPv6  12043      0t0  UDP *:51299
    cups-brow   720       root    8u  IPv4  14042      0t0  UDP *:631
    dnsmasq     779     nobody    4u  IPv4  14141      0t0  UDP osboxes:53
    dnsmasq     779     nobody    5u  IPv4  14142      0t0  TCP osboxes:53 (LISTEN)
    dhclient  10020       root    6u  IPv4  49773      0t0  UDP *:68
    beam.smp  10395       root   14u  IPv4  53494      0t0  TCP *:8003 (LISTEN)
    beam.smp  10414       root   14u  IPv4  52141      0t0  TCP *:8001 (LISTEN)
    beam.smp  10672       root   14u  IPv4  52145      0t0  TCP *:8002 (LISTEN)
    node      10863       root   12u  IPv6  52574      0t0  TCP *:8000 (LISTEN)
    mysqld    11243 messagebus   30u  IPv6  52694      0t0  TCP *:3306 (LISTEN)


Next installed the CLI

    wget https://s3-us-west-1.amazonaws.com/fastscore-cli/fastscore-cli-1.3.tar.gz
    tar xzf fastscore-cli-1.3.tar.gz
    cd fastscore-cli-1.3
    sudo python setup.py install

The first time I ran sudo python setup.py install I got the error.

    searching for websocket.client=0.37.0
    reading https://pypi.python.org/simple/websocket-client/
    error: [Errno 104] Connection reset by peer

I ran setuo again and it succeeded.  I suspect just a transient error but
am noting it in case its is repeatable.   It would be easy to continue from here
and not have the thing fully installed.

Next I created the `config.yml` file with:

    fastscore:
      fleet:
        - api: model-manage
          host: localhost
          port: 8002
        - api: engine-x
          host: localhost
          port: 8003

      db:
        type: mysql
        host: localhost
        port: 3306
        username: root
        password: root

This leaves off the kafka section.

And then submited it to fastscore via the CLI.

    fastscore connect https://localhost:8000
    fastscore config set config.yml

Note that the documentation says config.yml whens howing the content of the
file but the documentation says `fastscore config set config.yaml`  the extra
a is not wrong..its just a file name, but it is a subtle typo.

At this point you can get to the dashboard.  Make sure to use https instead of http.
http will not work.

    https://127.0.0.1:8000

## Get FastScore Running on DCOS

    #Todo: Add all the stuff I did for that.

## Tutorial: Gradient Boosting Regressor

These notes relate to the 'tutorial on [gradient boosting regressor](http://docs.opendatagroup.com/docs/example-gradient-boosting-regressor)

Requrements:
 * Python 2.7 - not mentioned specifically but I know.
 * NumPy
 * SciKit Learn
 * Kafka (python client)

##### Transforing Features

Preprocing of the input data.  `Fit` to normalize values, which helps
gradient boostng work.  `Transform` used during scoring to impute values based
 on mean variance and others determined from fit.

##### Train the Model

The training has the data included.

At the end of the section they said that you are going to send the
fitted model to the scoring, as well as the custom class, FeatureTransform.py


##### Loading the Model in FastScore

Steps:
 * Prepare model
 * input and output streams

Preparing the Model involves creating `action` method which is a generator
which `yield`s scores.   Also a `begin` method so that it can set itself up
and then accept may calls to `action`.

The input and output is specified in "smart comments"

If you look at `score_auto_gbm.py` there is no place where
`FeatureTransformer` is actually used...  #todo figure out where it gets used.


The Input and Output schemas are in Avro and there is a very specific
structure of them. Besides the schemas, there are Descriptors.. which
define the source and access.

##### Starting and configuring Fast Score

We should already be up.  But there is a note about Kafka that sez it is
up and there is a notify topic used by FastScore  for async communications.

One thing I didn't do in my config.yml is add the kafka section. I need to
do that.

Adding Packages to FastScore.. this is interesting.. this works with Compose:

    docker-compose exec engine-1 pip install pandas

There is a lot of details here for me to absorb. Its also an interesting
value to Sophia.

##### Creating the Attachment

To run this model you have the following defined:

 * `FeaturesTransform.py` custom transform class
 * `gbmFit.pkl` fitted model
 * `gbm-in.json` input stream descriptor
 * `gbm_input.avsc` input schema
 * `gbm-out.json` output stream descriptor
 * `gbm_output.avsc` output schema
 * `score_auto_gpm.py`  the scoring function.

 The fitted model and the custom class get `tar.gz`ed

 And then here are the commands to upload.

    fastscore schema add gbm_input gbm_input.avsc
    fastscore schema add gbm_output gbm_output.avsc
    fastscore stream add GBM-in gbm-in.json
    fastscore stream add GBM-out gbm-out.json
    fastscore model add GBM score_auto_gbm.py
    fastscore attachment upload GBM gbm.tar.gz

And then run

    fastscore job run GBM GBM-in GBM-out
    python kafkaesq --input-file /path/to/input/file.json input output

Where kafkasq is a provided executable that streams the content to the to input
and takes any output and puts it in a stream.

So fast score doesn't manage the entry into the streams.

How do you scale scoring?

Then there is a job stop.

    fastscore job stop GBM

## Sensors

Sensor Descriptors. 







