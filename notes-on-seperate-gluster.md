# Seperate Glusterfs run.

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







Dec 30 05:48:23 localhost.localdomain systemd[1]: Found ordering cycle on glusterd.service/start
Dec 30 05:48:23 localhost.localdomain systemd[1]: Found dependency on consul.service/start
Dec 30 05:48:23 localhost.localdomain systemd[1]: Found dependency on network-online.target/start
Dec 30 05:48:23 localhost.localdomain systemd[1]: Found dependency on glusterd.service/start
