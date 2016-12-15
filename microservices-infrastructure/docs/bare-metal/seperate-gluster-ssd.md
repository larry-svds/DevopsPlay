# Seperate Glusterfs run.


ansible-playbook -u lmurdock -K -i bare-metal/inventory -e @security.yml bare-metal/glusterfs-ssd.yml -v >& bare-metal/glusterfs-ssd.log

## Problems with 0.51 glusterd

1. consul gluster health checks give error:

        sudo: sorry, you must have a tty to run sudo

http://unix.stackexchange.com/questions/122616/why-do-i-need-a-tty-to-run-sudo-if-i-can-sudo-without-a-password

Checking the /etc/sudoers file there is the following comment.

        #
        # Disable "ssh hostname sudo <cmd>", because it will show the password in clear.
        #         You have to run "ssh -t hostname sudo <cmd>".
        #
        Defaults    requiretty

Commenting this line and rebooting does get you past the health check problem.

Should we uncomment this in sudoers or add the -t in the right place?

Where is the right place?

    - name: let consul use glusterfs commands for health checking
      sudo: yes
      template:
        src: consul-gluster-healthchecks.j2
        dest: /etc/sudoers.d/consul-gluster-healthchecks
      tags:
        - glusterfs


Fully spelled out in a control node the contents are:

    consul	ALL=(ALL)	NOPASSWD:	/usr/sbin/gluster pool list
    consul	ALL=(ALL)	NOPASSWD:	/usr/sbin/gluster volume info container-volumes


how do you add -t to that?

I have fixed this problem by running the following ansible accross the affected nodes.

       - name: remove default requiretty in sudoers so that consul healthchecks don't fail 1. add document line.
         sudo: yes
         lineinfile: dest=/etc/sudoers insertafter='^Defaults    requiretty' line="#Defaults    requiretty" state=present

       - name: remove default requiretty in sudoers so that consul healthchecks don't fail 2. remove default
         sudo: yes
         lineinfile: dest=/etc/sudoers regexp='^Defaults    requiretty'  state=absent

I'd be happy to do a pull request against mantl.io if we feel that is ok. Should it be done in
Common or Glusterfs?


2. /etc/systemd/system/glusterd.service.d/glusterd.conf

        [Service]
        After=consul.service dnsmasq.service
        Requires=consul.service dnsmasq.service

produces the following lines during startup.

        journalctl -u glusterd --reverse


gives:

        Dec 29 21:49:00 localhost.localdomain systemd[1]: [/etc/systemd/system/glusterd.service.d/glusterd.conf:2] Unknown lvalue 'After' in section 'Service'
        Dec 29 21:49:00 localhost.localdomain systemd[1]: [/etc/systemd/system/glusterd.service.d/glusterd.conf:3] Unknown lvalue 'Requires' in section 'Service'
        Dec 29 21:49:05 control01 systemd[1]: Starting GlusterFS, a clustered file-system server...


notice these happen before the machine gets a hostname.


The information in that file looks like what should be in the glusterd.service file under

after rebooting it didn't start.  So I `systemctl enable glusterd` and then rebooted and `systemctl status glusterd`
and got the following:

     glusterd.service - GlusterFS, a clustered file-system server
       Loaded: loaded (/usr/lib/systemd/system/glusterd.service; enabled; vendor preset: disabled)
      Drop-In: /etc/systemd/system/glusterd.service.d
               └─glusterd.conf
       Active: inactive (dead)

Turns out centos7 defaults to having all packages disabled for reboot.

The file `/usr/lib/systemd/system-preset\99-default-disable.preset` contains `disable *`  which means that all packages
that can be enabled for startup must be in a preset file.  Many packages are in preset files in this same directory.

glusterd is not.

useful links:
 * http://freedesktop.org/wiki/Software/systemd/Preset/
 * http://www.freedesktop.org/software/systemd/man/systemd.preset.html


Then I started looking at the order.  consul.service is After=network-online.target  and glusterd wants to be
Before=network-online.target



useful links:

## intro to run

I want to manage the glusterfs seperately for several reasons.
  * manage the docker pool and the gluster pool seperately
  * have separate pools for HD and SSD  i have 3 machines with SSD and 3 with HD


After a bunch of work.. I realized that they created 0.51 to fix glusterfs.

I built bare-metal/gluster-ssd.yml that adds 200Gb of SSD to a mount point.

I fdisked it..

Even with the 0.51 fix you still have this important step.

    Restarting
    ----------

    There is a bug with the current implementation where the glusterd servers will
    not come up after a restart, but they'll be fine to start once the restart is
    complete. To do this after a restart, run::

        ansible -m command -a 'sudo systemctl start glusterd' role=control

    You will also need to mount the disks after this operation::

        ansible -m command -a 'sudo mount -a' role=control


This is for use with docker and so this is how to load volumes with selinux watching.


    Use with Docker
    ---------------

    Any Docker volume should be able to access data inside the
    ``/mnt/container-volumes`` partition. Because of SELinux, the volume label needs
    to be updated within the container. You can use the ``z`` flag to do this, as in
    this example which will open up a prompt in a container where the volume is
    mounted properly at ``/data``::

        docker run --rm -it -v /mnt/container-volumes/test:/data:z gliderlabs/alpine /bin/sh



_Note_ I called in /mnt/container-volumes-ssd  cause I want to provide that and
a hd version.


