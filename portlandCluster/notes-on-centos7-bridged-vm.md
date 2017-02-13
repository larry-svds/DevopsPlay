# Setting up Centos 7.2 base VMs.  

First there install: 

 * virtual box
 * From the App Store `Dr Uncarchiver`
 * Grab the Centos 7.2 virtual box from http://www.osboxes.org/centos/
 * I just opend the virtual box 1611 in the downloads directory. 
 * Create Virtual box
    * Name: DCOS-Boot,  Type: Linux, Version: Red Hat (64-bit)  (The other 4 Created are Master Pub-Agent and Pri-Agent)
    * Memory: 6507
    * Use Existing Virtual hard disk file. Search to:  Downloads/1611-64bit/CentOS 7-1611 (64bit).vdi
    * This creates a 100G machine. 
    * Root User is osboxes.org with password osboxes.org
    
Not sure where I missed the setings for cores, but i had to go back.stop each machine and then change Cores 
to two.
    
##### adding the Centos sudoer user

    sudo adduser centos
    sudo passwd centos
    sudo usermod -aG wheel centos
    
I tested it with 
    
    su - centos
    sudo visudo
    
and then edited wheel line so that oyu don't have to put in a password for sudo for wheel users. 

    %wheel ALL=(ALL)    NOPASSWD: ALL

##### Adding keyless access to Centos user. 


    cd ~
    mkdir .ssh
    cp id_rsa .ssh
    cp id_rsa.pub .ssh
    cat id_rsa.pub >> .ssh/authorized_keys 
    chmod 700 .ssh
    chmod 640 .ssh/authorized_keys

you can then test it with `ssh -i ~/.ssh/rsa_id centos@172.16.222.119`

Side note.. I had done this after the fact. So I had ot do it to all 4 vms.  I could have used 
ansible.. but I just used the tmux program that does everthing in paralell that Mark Mims showed me. 

So 

    cd ~/src/mark
    ./tmux-cssh centos@172.16.222.119 centos@172.16.222.120 centos@172.16.222.125 centos@172.16.222.135
    
you can get usage with just entering `./tmux-cssh`

The contents of that script are [here](notes-on-centos7-nuc.md) in the "How I work on 6 machines at a time"
section. 

##### Adding Guest Additions

 * Add guest additions to the Mac Virtual Box....  Not really sure why.. It was super sketchy and annoying.

       cp /Applications/VirtualBox.app/Contents/MacOS/VBoxGuestAdditions.iso ~

 * at this point its sitting in /Users/lmurdock  I have to close down the vm and then
    * under vm settings I can add an optical drive under sata.  And chose a file and chose the iso.  
    * restart the vm.  
 * Add guest additions from command line. open a terminal
       
          sudo yum update
          sudo yum install gcc make kernel-devel bzip2
          sudo mkdir -p /media/cdrom
          sudo mount /dev/sr0 /media/cdrom
          sudo sh /media/cdrom/VBoxLinuxAdditions.run

Kinda wish I wasnt installing all this on the OS.  but I need guest additions to not have mouse capture, 
because it doesn't work well with remote screen share.


##### Making Static IPs on Centos in Virtual Box

Set it to bridge mode network in the VM settings in virtual box. And ran it. 

ifconfig showed a ip in my 172.16.222.x range.

Went to the Verizon Router.  

Found the VM in Connected Devices.  Edited it and gave it an IP IN THE DHCP RANGE.  so 119 in the first vm.  

Then on the vm in a bash window

    nmcli con
    nmcli con down id "Wired connection 1" 
    nmcli con up id "Wired connection 1"
    
The string "Wired connection 1" was listed in the first command as the name of the bridged network. 

After this `ifconfig` showed 172.16.222.119 


    
##### Clone the machine

Right click on a stopped machine will give you a clone option. give it the new name.. and also be sure 
to chec the Reinitialize MAC Address of all network cards.  This is essential if you are going to run 
the clone in the same network, as it gives the network cards unique mac ids.

I created a full clone so I could move it to another machine. also its just easier. When you create a linked 
clone it means odd things.  I have diskspace.. I cloned full.

After copying it over.. I had it in a download directory.. then I created a vm in my virtual box and added the 
vdi from that directory when chose "use existing".  Once that was made a Created two clones with "reinitialize
the MAC Address".

When I do copy it over.. I need to do a full clone again, since I need new mac addresses, since the second 
machine is also in the same network.  Then I can link clone the 4th instance. And finally delete the copy 
I sent over from the other machine. 

I also noticed that when I created the machine from scratch my router recognizes it by its name.. but when I 
create a clone my router just shows it by mac address. 

You can find the mac address of the cloned vm in the advanced table of settings/network for your 
bridged adapter. 


#####  Set the name on each box

    hostnamectl set-hostname x.y.z
    
