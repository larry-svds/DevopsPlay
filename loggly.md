## setup
I created an account svds.loggly.com
user lmurdock
our key is "c1e6035f-cd4b-4b61-9f2c-968019ec90b0"

Went to logstash setup

https://svds.loggly.com/sources/setup/logstash

they say go to outputs directory..

    cd logstash-1.4.2/lib/logstash/outputs
    sudo wget https://raw.githubusercontent.com/psquickitjayant/logstash-output-loggly/master/lib/logstash/outputs/loggly.rb

To get to that on the the docker image I had to look at the dockerfile

https://hub.docker.com/r/ciscocloud/logstash/~/dockerfile/

and then since I didn't know what the $GEM_PATH was I had to do

    find /opt -name "logstash-core*"

which then adding all the stuffs from there instructions I got

    root@resource01:/opt/logstash/vendor/bundle/jruby/1.9/gems/logstash-core-1.5.3-java/lib/logstash/outputs# ls
    base.rb  loggly.rb

but.. it gets reloaded at the start of the run.

None of that actually worked.  

I am headed down the rsyslog path now and that is sucking because of the assumption loggly makes about initd... so
learning to make work.. some how.

Cool commands.  

    nmcli d show

shows all your network

Oh man.. so many things changed.

look in the directory ~/src/LarryMantl/tryloggly  The file rsyslog.conf was copied to all /etc/rsyslog.conf
locations.  the 22-loggly.conf was copied to all the /etc/rsyslog.d/ directories.

Each /etc/hosts was changed to have the host name before the localhost so that
log entries would have meaningful hosts and not localhost.  This is per
https://wiki.archlinux.org/index.php/Rsyslog

There is also the fact that all the times are set to UTC for localtime.. this was annoying so..

  sudo rm /etc/localtime
  sudo ln -s /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

I think there was a copied file from mantl.io  there is a date time ctl program that
gave me selinux problems.  this is what caused me to go ahead and softlink.
