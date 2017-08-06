# Install nfs server on Portland Cluster

Control01 will run nfs and serve out the common mnt directories in the cluster. 


### On Server

So Control01 will serve out a directory that everyone will load as  `/mnt/nfs`

THe directory I am using is `/home/nfs` which is happening becuase the bulk of 
the ssd is in the partition devoted to `/home`.

    ssh control01
    
    sudo yum -y install nfs-utils
    sudo systemctl enable nfs-server.service
    sudo systemctl start nfs-server.service
    
    sudo mkdir /home/nfs
    sudo chown nfsnobody:nfsnobody /home/nfs
    sudo chmod 755 /home/nfs
    
    sudo vi /etc/exports
    
and add
    
    /home/nfs        172.16.222.0/24(rw,sync,no_subtree_check)

then
    
    sudo exportfs -a
    

### ON Clients
    
    sudo yum -y install nfs-utils
    
    sudo mkdir -p /mnt/nfs
    sudo mount 172.16.222.6:/home/nfs /mnt/nfs

 on macos you may need to do this.

    sudo  mount_nfs -o resvport 172.16.222.6:/home/nfs /mnt/nfs

Not sure why it works.. but it does.  From here. https://thornelabs.net/2013/10/15/operation-not-permitted-mounting-nfs-share-on-os-x-mountain-lion.html

## Unable to chown locally with sudo. 

THere is a security issue with this but it does make it work a bit easier in a dev 
environment. 

exports are defaulted to root_squash so you have 
[this problem](http://serverfault.com/questions/212178/chown-on-a-mounted-nfs-partition-gives-operation-not-permitted)
Solution is to add `no_root_squash`  so 
back on `control01` I changed `/etc/exports` one more time adding the option 
and the reran `exportfs -a`

    /home/nfs        172.16.222.0/24(rw,sync,no_subtree_check,no_root_squash)