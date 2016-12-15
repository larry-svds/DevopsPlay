

https://www.howtoforge.com/nfs-server-and-client-on-centos-7

Which errors out on systemctl enable nfs-lock and systemctl enable nfs-idmapd.service
So I also followed
https://www.centos.org/forums/viewtopic.php?f=47&t=53896

Install the packages as follows:

    yum install nfs-utils

Now create the NFS directory mount point as follows:

    mkdir -p /mnt/nfsshare

Start the services and add them to boot menu.

    systemctl enable rpcbind
    systemctl enable nfs-server
    systemctl enable nfs-lock
    systemctl enable nfs-idmap

But this fails with
    systemctl enable nfs-lock Failed to issue method call: No such file or directory
    systemctl enable nfs-idmap Failed to issue method call: No such file or directory

so

edit `/usr/lib/systemd/system/nfs-idmap.service`   and at the bottom enter:

    [Install]
    WantedBy=multi-user.target

to the new override file.


edit `/usr/libsystemd/system/nfs-lock.service` and at the bottom enter:

    [Install]
    WantedBy=nfs.target

Next you

    systemctl enable nfs-idmapd.service
    systemctl enable rpc-statd.service

note that that is not the same as what you have been editing.

Then finally.  

    systemctl start rpcbind
    systemctl start nfs-server
    systemctl start nfs-lock
    systemctl start nfs-idmap

Next we will mount the NFS shared content in the client machine as shown below:


    mount -t nfs 172.16.222.14:/var/nfsshare /mnt/nfsshare
