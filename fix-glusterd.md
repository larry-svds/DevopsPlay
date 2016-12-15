

#### Issue #872 Getting Glusterd booting and mounting filesystems on startup.

Changes:
  * edited glusterd.conf
  * moved glusterd.conf to role/glusterd/file
  * changed template glusterd.conf to copy glusterd.conf (because it is now in files)
  * added gluster.service file to /files .  This is the default file with Before section commented out.
  * added copy command to move that file to /etc/systemd/system


First thing I noticed was that


    journalctl -u glusterd --reverse

produced


    Dec 30 06:39:36 control02 systemd[1]: Failed to start GlusterFS, a clustered file-system server.
    Dec 30 06:39:36 control02 systemd[1]: glusterd.service: control process exited, code=exited status=1
    Dec 30 06:39:05 control02 systemd[1]: Starting GlusterFS, a clustered file-system server...
    Dec 30 06:39:00 localhost.localdomain systemd[1]: [/etc/systemd/system/glusterd.service.d/glusterd.conf:3] Unknown lvalue 'Requires' in section 'Service'
    Dec 30 06:39:00 localhost.localdomain systemd[1]: [/etc/systemd/system/glusterd.service.d/glusterd.conf:2] Unknown lvalue 'After' in section 'Service'

Looking at that file I realized that Section `Service` was suppose to be section `Unit`

Rebooting this time I got no errors but the service didn't even try to start.
Looking at the dependencies I noticed that glusterd was Before=network-online.target
and we were adding Requires=consul.service  which in turn has an After=network-online.target

I read in several places that you could nullify ExecStart by having a line `ExecStart=`
so I tried that with `Before=` .  So now `/etc/systemd/system/glusterd.service.d/glusterd.conf`
is:

      [Unit]
      After=consul.service dnsmasq.service
      Requires=consul.service dnsmasq.service
      Before=

This time a reboot at least confirmed that we were dealing with incompatible dependencies.

    Dec 30 06:31:30 localhost.localdomain systemd[1]: Found ordering cycle on glusterd.service/start
    Dec 30 06:31:30 localhost.localdomain systemd[1]: Found dependency on consul.service/start
    Dec 30 06:31:30 localhost.localdomain systemd[1]: Found dependency on network-online.target/start
    Dec 30 06:31:30 localhost.localdomain systemd[1]: Found dependency on glusterd.service/start

But the `Before=` did not fix the problem.

    [centos@control03 ~]$ systemctl show -p Before glusterd
    Before=glusterfsd.service shutdown.target multi-user.target network-online.target

I tried adding a line after the empty Before= with `Before=nfs-client.target` but that
did not help to erase the network-online.target dependency.  It just added a dependency to
nfs-client.target.  I chose that cause it was a service that was kinda after everything.

The only real solution is to comment out the Before line in the actual glusterd.service
file.  You are not suppose to do that in the multi-user.target.wants directory.  
So I took a copy of it commented out the Before and placed it in `/etc/systemd/system`
where you are suppose to put edited unit files.  

Rebooting gave me a working system with glusterd running and file systems mounted.
