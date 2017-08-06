# notes on AWS setup md

### On April 17 we started the web console

    ssh -i ~/.ssh/awsmadsen.pem -nNT -L 8888:localhost:8888 centos@34.209.52.63

do that in a shell.

then your browser should show you the nuodb web console on localhost:8888


###  A few things I did that I should doc.

grabbed standard centos 7.3 distro.
Got rid of the thb

##### Logs are in /var/log/nuodb



##### Disable SELinux

    sudo vi /etc/selinux/config

set it to permisive.

##### The Nuodb WebConsole is only enabled for Localhost.

Create a ssh tunnel

     ssh -i ~/.ssh/awsmadsen.pem -nNT -L 8888:localhost:8888 centos@52.43.27.16

then open your browser to localhost:8888


### If you get the error about Stable_ID

http://doc.nuodb.com/Latest/Content/Broker-Startup-Failure-Cannot-Peer-to-Duplicate-StableId.htm


##### Kill the cfg directory

    sudo rm -rf /etc/nuodb

##### Kill the Raft Directory

    sudo rm -rf /var/opt/nuodb/Raft


### Default.properties file..

So many changes for AWS.. see this page
http://doc.nuodb.com/display/doc/Deploy+with+Amazon+Web+Services

And then below you can see how I interpreted this.

This file is for the second host.  the peer host is the other host that
was started with `peer=`  set to blank.

Not that I peered them on the internal ip. This corresponds with what

    hostname --fqdn

returns.

Also I did not have to mess with `/etc/hosts` because if you are using these
ec2 provided names. they are all in the dns servers that these systems are
using.


    # Copyright (C) NuoDB, Inc. 2012-2015  All Rights Reserved.
    #
    # The default agent properties. To use a different source of properties set
    # the system property "propertiesUrl" to the URL of a properties file:
    #
    #   java -DpropertiesUrl=URL nuoagent.jar ...
    #
    # The default values for each property are shown in this file. All addresses
    # can optionally include a port number using the syntax host:port.
    #
    # Note that all of these properties are optional, except for the domain
    # password. A default value is assigned to this. Domain administrators should
    # pick a new password to secure their domains.
    #
    # 2.0 History:
    #
    # 2.0.1
    #   "metricsPurgeAge", "eventsPurgeAge" added
    # 2.0.2
    #   "automationTemplate" added
    # 2.0.3
    #   "automationTemplate": Once the admin db has been created during bootstrap,
    #       use Auto Console UI to edit the admin db's template. The bootstrap
    #       process will no longer upgrade the template as it did in 2.0.2
    #   "peer" supports comma-separated list of peers
    # 2.0.4
    #   "agentPeerTimeout", "hostTags" added (optional)
    #   "singleHostDbRestart" added, default TRUE
    # 2.0.5
    #    added support for policy "balancer=AffinityBalancer"
    # 2.1
    #   removed default "domainPassword"
    #   added "removeSelfOnShutdown"
    #   revised "heartbeatPeerTimeout"
    #   Automation, managed databases:
    #   * added "enableSystemDatabase"
    #   * added "schEnforcerPeriodSec, schEnforcerInitDelaySec, runEnforcerOnEveryEvent"
    #   * revised/deprecated "enableAutomation"
    #   * removed "enableAutomationBootstrap", "enableHostStats", "eventsPurgeAge"
    #
    #   The "peer" property has been changed for brokers:
    #   * A broker no longer supports a comma-separated list of peers
    #   * A broker now supports its own address as peer attribute (peer to self)
    #
    #   added "RaftHeartbeatTimeout", "RaftMinElectionTimeout", "RaftMaxElectionTimeout"
    #
    # 2.1.1
    #   added "RaftLogCompactionThreshold"
    #   updated documentation for balancer property
    #
    # 2.2.1
    #   property "heartbeatPeerTimeout" behavior change; hangup the connection
    #     with the other peer if the ping timeout was reached.
    #
    # 2.4
    #   new default, property removeSelfOnShutdown=false
    #   new default, property processStartWaitBarrier=All
    #   new default, property RaftLogCompactionThreshold = 512
    #
    # 2.5.4
    #   added property "nodeStartTimeoutSec". Defaults to 30 seconds.

    # The default administrative password, and the secret used by agents to
    # setup and maintain the domain securely
    domainPassword = bird

    # The name used to identify the domain that this agent is a part of
    domain = domain

    # A flag specifying whether this agent should be run as a connection broker
    broker = true

    # The port that this agent listens on for all incoming connections
    port = 48004

    # An existing peer (agent or broker) already running in the domain that this
    # agent should connect to on startup to extend the running domain. All brokers
    # should be peered with the same broker. On restart, a broker will first try
    # to connect to the broker per this "peer" setting; if it is unreachable, the
    # broker will fall back to its last-known state of brokers.
    # An agent will accept a comma-separated list of peers. A broker doesn't.
    peer =

    # An alternate address to use in identifying this host, which is not actually
    # advertised unless the advertiseAlt property is set.
    altAddr =ec2-52-43-27-16.us-west-2.compute.amazonaws.com

    # A flag specifying whether the alternate address should be advertised instead
    # of the locally observed network addresses. This is only meaningful for
    # brokers, because only brokers advertise addresses to clients and admins.
    advertiseAlt = true

    # The region for this host. The region of a host should not be changed after it
    # has been set.
    region ="us-west-2"

    # The log level for the agent log output. Valid levels are, from most to least
    # verbose: ALL, FINEST, FINER, FINE, CONFIG, INFO, WARNING, SEVERE, OFF
    #log = INFO

    # The location of the directory with the 'nuodb' executable, which is typically
    # the same as the directory where the nuoagent.jar file is found
    #binDir = .

    # A range of port numbers that nuodb instances should be confined to. This is
    # of the form start[,end].  Note: Specifying a start without an end indicates
    # that process TCP/IP ports are assigned incrementally from the start without
    # limit
    #
    # Each new process (transaction engine or storage manager) that is started on a
    # machine is communicated with via an assigned TCP/IP port that is specified
    # via this property.  Ensure firewall rules allow access from other machines.
    portRange = 48005

    # Deprecated.
    # A flag specifying whether this host has automation enabled. The behavior has
    # changed in that automation no longer depends on the "nuodb_system" admin
    # database, which is now optional. All agents and brokers in the domain should
    # have the same value.
    #enableAutomation = true

    # The interval (in seconds) that brokers should wait between sending out UDP
    # broadcast messages for local discovery, and that agents should wait to hear
    # those messages on startup. By default broadcast is turned off so peering
    # is done using the 'peer' property.
    #broadcast = 0

    # A flag specifying whether nuodb instances can only be started through this
    # agent (as opposed to directly starting a nuodb process on the system). If this
    # flag is true then a "connection key" is required of all nuodb instances. A
    # connection key is only available if the process was started through a request
    # on the agent. This is a good best-practice flag for locking down a system.
    requireConnectKey = true

    # A property specifying the SQL connection load balancer that this Broker
    # should use. The balancer determines how the Broker chooses which Transaction
    # Engine (TE) to use for an SQL client connection. This property has no effect
    # on an Agent.
    # The balancer property can be set to one or more load balancer policies
    # separated by commas. For more information, see
    # http://doc.nuodb.com/Latest/Default.htm#Balancing-Database-Load-Across-Hosts.htm
    #
    # Available load balancers are:
    # RoundRobinBalancer
    # ChainableModBalancer
    ChainableRegionBalancer
    # ChainableTagBalancer
    # ChainableLocalityBalancer
    # ModBalancer (deprecated)
    # RegionBalancer (deprecated)
    # AffinityBalancer (deprecated)
    #balancer =

    # ADDED in 2.0.1 #

    # When "enableAutomation" is set, prune metrics by age. Default is 12 hours: 12h
    # Supported Units are d=day, h=hour, m=minute.
    #metricsPurgeAge = 12h

    # ADDED in 2.0.2 #

    # If "enableSystemDatabase" is enabled, then use this template to enforce
    # the NuoDB "nuodb_system" admin database.
    # REVISED in 2.0.3:
    # Once admin db is created during bootstrap, use Auto Console UI to edit
    # the admin db's template.
    #automationTemplate = Single Host

    # ADDED in 2.0.4 #

    # By default, an agent will shutdown when the peer attempt failed. By setting
    # this property, the agent will continue to try to entry peer, until the timeout
    # in milliseconds has been reached. To preserve backward compatibility, the default
    # is to not retry. Note that this option is not related to agent reconnect when
    # its peer broker disconnects; this option is only for the initial entry into the
    # domain.
    #agentPeerTimeout = -1

    # This property enables auto-restart of single host databases. The broker
    # writes a marker file into the varDir (e.g. /var/opt/nuodb1/demo-archives/)
    # when a database starts up. On machine / broker restart, the broker starts
    # any database for which a marker exists. A database shutdown command will
    # remove the marker. Only applicable for "un-managed" databases not governed
    # by Automation.
    # Code default is false, to preserve backward compatibilty
    # singleHostDbRestart = false
    singleHostDbRestart = true

    # Set this property to inject additional Host Tags into the agent's TagService.
    # Well-defined host tags that are injected by default such as "osversion", "region"
    # can not be overwritten and will be ignored. The format is a comma-separated list
    # of key=value pairs, with each string token being trimmed.
    # Example: hostTags = tag1 = val, tag2=v2
    #hostTags =

    # ADDED in 2.1 #

    # Set this property to true if a broker JVM termination (kill -TERM, including
    # service restart) should remove itself from the durable domain configuration.
    # The default value has been changed in 3.0.
    removeSelfOnShutdown = true

    # If this property is set to true, the broker(s) will provision the optional
    # database "nuodb_system" in the domain. Among other things, it stores
    # persistent metrics on hosts and database processes which are available both in
    # the Automation Console UI as well as the Rest API. This database is managed,
    # and will be automated using the template per the above "automationTemplate"
    # property. If it's not provisioned automatically here during broker startup,
    # it can always be created later using managed database creation.
    enableSystemDatabase = true

    # There are three timeout value properties that can be adjusted if Raft
    # leadership is not stable. As a general set of rules:
    # 1. RaftHeartbeatTimeout should be significantly higher than the latency
    # 2. RaftMinElectionTimeout should be significantly higher than the
    #    RaftHeartbeatTimeout
    # 3. RaftMaxElectionTimeout should be higher than RaftMinElectionTimeout
    # If elections are being triggered too often the RaftHeartbeatTimeout and/or
    #  the RaftMinElectionTimeout should be increased (maintaining the above rules).
    # If elections take too many rounds to be resolved (lots of "Converting to
    #  Candidate" with no "Converting to Leader") the difference between
    #  RaftMinElectionTimeout and RaftMaxElectionTimeout should be increased
    #  (likely by increasing RaftMaxElectionTimeout).
    # timeouts are in ms
    #RaftHeartbeatTimeout = 500
    #RaftMinElectionTimeout = 4100
    #RaftMaxElectionTimeout = 8300

    # Enforcer schedule properties: the Enforcer runs periodically in the Broker
    # that is the current Leader, by default every 10 seconds, with an initial delay
    # of 15 seconds after the Broker starts up. Each Enforcer run performs at most
    # one process start per database.
    # By default, most domain events (Agent joins/leaves, database engine process
    # joins/leaves, update to a database template etc) call the Enforcer directly
    # regardless of the schedule. This is useful in development/demo mode but should
    # be disabled in production.
    #schEnforcerPeriodSec = 10
    #schEnforcerInitDelaySec = 15
    #runEnforcerOnEveryEvent = true

    # Every update to the Broker's durable domain state causes a "log entry". This
    # property allows you to set a max number of entries to be stored in the
    # log. When the Broker starts, it reads all log entries to compute the current
    # set of state-machines. This can get expensive if you have a large number of
    # entries, which are also held in memory. The default behavior is to leave the
    # threshold high to provide backward compatibility; otherwise rolling upgrade
    # might break if a new Broker sends information to an older Broker. It is
    # recommended that a customer should set this property to a lower number.
    #RaftLogCompactionThreshold = 512

    # Agent/Broker ping their connected peer(s) periodically. A warning is printed
    # if we don't hear a ping-ack after 10 seconds, and then continuously after that
    # until the timeout.
    # Setting "heartbeatPeerTimeout" to a value larger than 0 will hangup the
    # connection with the other peer if the ping timeout was reached. The default
    # value is 45s (10min prior to 2.4). In previous releases, after the ping
    # timeout was reached, only the WARN stopped being logged but the connection was
    # not severed.
    # Use value > 0 for timeout to go into effect; 0 means wait forever, don't
    # timeout.  Choose a value higher than "RaftMaxElectionTimeout".
    #heartbeatPeerTimeout = 45

    # Setting the process start barrier ensures safety against split-braining a
    # database. When an Agent/Broker restarts, it will take up to 10s for any local
    # process to reconnect to it. An Agent/Broker will run a Domain State Machine
    # (DSM) Resync protocol to remove process entries that weren't removed when
    # database processes shutdown while the local Agent/Broker was NOT running; on
    # restart, the Agent/Broker first waits for processes to reconnect, then
    # reconciles to PID list with the process entries in the DSM. Starting an engine
    # process is only allowed after the process reconnect window and the DSM
    # Resync. See also the section "Process Barriers" in the Documentation. The
    # default value is to enable the barrier for managed and un-managed database.
    #processStartWaitBarrier = All

    # Defines how long the Enforcer will wait, in seconds, for a new process to start
    # before trying to start other processes.
    #nodeStartTimeoutSec=30
