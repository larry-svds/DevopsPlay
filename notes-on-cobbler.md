# Setting Up Cobbler on Centos 7

Working from this.

http://www.olindata.com/blog/2015/07/cobbler-setup-centos7

Turning off firewalld

      systemctl stop firewalld
      systemctl disable firewalld

Disable selinux by editing /etc/selinux/config and setting SELINUX=disabled

or permissive.

      sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

already installed.

    sudo yum install cobbler cobbler-web dnsmasq syslinux pykickstart

bunch of output and then:

    Installed:
      cobbler.x86_64 0:2.6.11-1.el7          cobbler-web.noarch 0:2.6.11-1.el7
      syslinux.x86_64 0:4.05-12.el7

    Dependency Installed:
      mod_ssl.x86_64 1:2.4.6-40.el7.centos
      python-cheetah.x86_64 0:2.4.4-5.el7.centos
      python-django.noarch 0:1.6.11-4.el7
      python-django-bash-completion.noarch 0:1.6.11-4.el7
      python-markdown.noarch 0:2.4.1-1.el7.centos
      python-pillow.x86_64 0:2.0.0-19.gitd1c6db8.el7
      python-pygments.noarch 0:1.4-9.el7
      python-simplejson.x86_64 0:3.3.3-1.el7
      tftp-server.x86_64 0:5.2-12.el7

    Updated:
      dnsmasq.x86_64 0:2.66-14.el7_1        pykickstart.noarch 0:1.99.66.6-1.el7

    Dependency Updated:
      httpd.x86_64 0:2.4.6-40.el7.centos    httpd-tools.x86_64 0:2.4.6-40.el7.centos

    Complete!

Start the Cobbler Services.

    sudo systemctl enable cobblerd
    sudo systemctl start cobblerd
    sudo systemctl enable httpd
    sudo systemctl start httpd


## Fight with cobbler_web permission problem

You then go to `https://172.16.222.14/cobbler_web` where I got:

    Forbidden

    You don't have permission to access /cobbler_web on this server.

The web site is located in /var/www/cobbler_webui_content.

The configuration is in /etc/cobbler/settings

This turned out to be becasue of messed up /etc/host and network settings.  The error was logged in
`/var/log/httpd/error_log` as:

    AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using 10.0.1.13. Set the 'ServerName' directive globally to suppress this message

nope.. but that was good to fix anyways.

The request is getting to http.. but the access to cobber_web is resulting in a 403.

The path `cobbler_web` is not in `/var/www`, after some searching.. it is configured in
`/etc/httpd/conf.d/cobbler_web.conf`

Hitting https://jump and http://jump works and you get a test page.  This points out that you
don't have a index.html in `/var/www/html/index.html`.

Hitting https://jump/cobber_web get you

    [Sat Feb 27 01:47:13.126555 2016] [ssl:error] [pid 2405] [client 172.16.222.100:61683] AH02219: access to /usr/share/cobbler/web/cobbler.wsgi failed, reason: SSL connection required


eventually I set the ServerName to jump:443 in /etc/httpd/conf/httpd.conf and commented out

    <Directory "/usr/share/cobbler/web/">
    #LMM
    #        <IfModule mod_ssl.c>
    #            SSLRequireSSL
    #        </IfModule>
    #        <IfModule mod_nss.c>
    #            NSSRequireSSL
    #        </IfModule>
            SetEnv VIRTUALENV
            Options Indexes MultiViews
            AllowOverride None
            Order allow,deny
            Allow from all
    </Directory>

    <Directory "/var/www/cobbler_webui_content/">
    #LMM
    #        <IfModule mod_ssl.c>
    #            SSLRequireSSL
    #       </IfModule>
    #       <IfModule mod_nss.c>
    #           NSSRequireSSL
    #       </IfModule>
            Options +Indexes +FollowSymLinks


            AllowOverride None
            Order allow,deny
            Allow from all
    </Directory>


In `/etc/httpd/conf.d/cobbler_web.conf`

I believe the self signed certs are working.. they are encrypting traffic but perhaps this setting
has a stronger requirement?  I don't know its not that big of a problem for me in my house.

have to keep an eye out if I can't server content.

Checking my cert was interesting..

http://serverfault.com/questions/578061/rsa-certificate-configured-for-server-does-not-include-an-id-which-matches-the-s

To get to it I had to see this one:

https://www.digicert.com/ssl-certificate-installation-apache.htm

it was in /etc/httpd/conf.d/ssl.conf and the file is located here `/etc/pki/tls/certs/localhost.crt`

## Cobbler Templates Jinja2 or cheetah

I just wanted to make a note that you can pick jinja2 for templating. It defaults to cheetah but
jinja is what we are using with ansible.

## DNS and DHCP

Cobbler can manage your DNS and DHCP through dnsmasq

The article does this.  We don't want to.  Our DNS and DHCP is going to be driven from our
cluster and terraform work.  So we need to set up dnsmasq ourselves.

But perhaps having this be the source of truth for a new hardware piece is fine.

Looking at `/etc/cobbler/dhcp.template` encourages me to follow their plan over trying to
do it right.

    /etc/cobbler/settings:
    default_password_crypted: "{I left it the standard cobbler cobbler}"
    manage_dhcp: 1
    manage_dns: 1
    pxe_just_once: 1
    next_server: 172.16.222.14
    server: 172.16.222.14

The document said set `pxe_just_once: 1`  but when I read this in the settings file I decided
 not to because I don't want to set my machines to pxeboot. I don't think I do anyways.. here
 is the comment in the settings file. See NOTE after.

    # if this setting is set to 1, cobbler systems that pxe boot
    # will request at the end of their installation to toggle the
    # --netboot-enabled record in the cobbler system record.  This eliminates
    # the potential for a PXE boot loop if the system is set to PXE
    # first in it's BIOS order.  Enable this if PXE is first in your BIOS
    # boot order, otherwise leave this disabled.   See the manpage
    # for --netboot-enabled.
    pxe_just_once: 1

NOTE Later I changed my mind after reading  http://cobbler.github.io/manuals/2.4.0/4/1/3_-_Systems.html about -netboot-enabled

So I did set it to 1.

I also set `bind_master: 172.16.222.14`  per https://hcc-docs.unl.edu/pages/viewpage.action?pageId=2851383

then modules config to dnsmasq

    /etc/cobbler/modules.conf
    [dns]
    module = manage_dnsmasq

    [dhcp]
    module = manage_dnsmasq

And finally dhcp.template.  This file generates dhcpd.conf.

    subnet 192.168.1.0 netmask 255.255.255.0 {
         option routers             192.168.1.5;
         option domain-name-servers 192.168.1.1;
         option subnet-mask         255.255.255.0;
         range dynamic-bootp        192.168.0.4 192.168.0.25;
         default-lease-time         21600;
         max-lease-time             43200;
         next-server                $next_server;
         class "pxeclients" {
              match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";
              if option pxe-system-type = 00:02 {
                      filename "ia64/elilo.efi";
              } else if option pxe-system-type = 00:06 {
                      filename "grub/grub-x86.efi";
              } else if option pxe-system-type = 00:07 {
                      filename "grub/grub-x86_64.efi";
              } else {
                      filename "pxelinux.0";
              }
         }

    }

This just freaks me out.. almost all of this is exactly the same.  But in the document
for subnet 192.168.1.0 netmask 255.255.255.0 they have a:

    range dynamic-bootp        192.168.0.4 192.168.0.25;

Which is not in the same subnet.. AND it overlaps with the `option routers 192.168.1.5;` and
default in the file looks way more reasonable.

    range dynamic-bootp        192.168.1.100 192.168.1.254;

Not much is described here but the paper keeps showing 192.168.0.* usage all the way to screen
shots.

Also what is that routers option?   A bit of googling got me to https://hcc-docs.unl.edu/pages/viewpage.action?pageId=2851383

    subnet 192.168.1.0 netmask 255.255.255.0 {
         ## You must change the options routers to the IP of the gateway device. ##
         ## In this case, its the IP of the cobbler head node ##
         option routers             192.168.1.1;

         ## The domain-name-servers option must be changed so that the IP of the new BIND server we've setup through cobbler ##
         option domain-name-servers 192.168.1.1;

         ## Domain name of the cluster as served through DHCP. MUST be the value set in /etc/cobbler/settings manage_forward_zone option ##
         option domain-name         "example.com";
         option subnet-mask         255.255.255.0;
         range dynamic-bootp        192.168.1.10 192.168.1.149;
         filename                   "/pxelinux.0";
         default-lease-time         21600;
         max-lease-time             43200;
         next-server                $next_server;
    }

That explains a bit.  Perhaps the 192.168.0.x works because dnsmasq can manage whatever range it
wants to.  I wonder too though.. was the document implicitly saying that its own IP is
192.168.1.1?  Thats a pretty rare thing. So I am thinking that the original article didn't get it all
right.


So I did this.

    subnet 172.16.222.0 netmask 255.255.255.0 {
         ## You must change the options routers to the IP of the gateway device. ##
         ## In my case that is the gateway device.
         option routers             172.16.222.1;

         ## The domain-name-servers option must be changed so that the IP of
         #the new BIND server we've setup through cobbler ## In my case DNSMASQ Server
         option domain-name-servers 172.16.222.14;
         option subnet-mask         255.255.255.0;
         range dynamic-bootp        172.16.222.6 172.16.222.99;
         default-lease-time         21600;
         max-lease-time             43200;
         next-server                $next_server;
         class "pxeclients" {
               match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";
               if option pxe-system-type = 00:02 {
                       filename "ia64/elilo.efi";
               } else if option pxe-system-type = 00:06 {
                       filename "grub/grub-x86.efi";
               } else if option pxe-system-type = 00:07 {
                       filename "grub/grub-x86_64.efi";
               } else {
                       filename "pxelinux.0";
               }
         }
    }

Some notes about as I try to pull this together.  My gateway device does dhcp and gives out
addresses from 100-255.  I am hoping it doesn't get in the way of this dnsmasq which is doing
dynamic from 6 to 99 (which will be assinged specific IPs per mac.)

NOTE: HIGH POTENTIAL ERROR  ^

I also just dropped the `option domain-name` as it was not in the original article and may be
 related to BIND.

finally I left the current default of a much more complex `filename` resolution from the file
on my system and the main document I am following


Then `/etc/cobbler/dnsmasq.template`:

    # Cobbler generated configuration file for dnsmasq
    # $date
    #

    # resolve.conf .. ?
    #no-poll
    #enable-dbus
    read-ethers
    addn-hosts = /var/lib/cobbler/cobbler_hosts

    dhcp-range=172.16.222.6,172.16.222.99
    dhcp-option=3,$next_server
    dhcp-lease-max=1000
    dhcp-authoritative
    dhcp-boot=pxelinux.0
    dhcp-boot=net:normalarch,pxelinux.0
    dhcp-boot=net:ia64,$elilo

    $insert_cobbler_system_definitions


And now .. try things out.

    sudo systemctl restart cobblerd
    cobbler check


    1 : change 'disable' to 'no' in /etc/xinetd.d/tftp
    2 : some network boot-loaders are missing from /var/lib/cobbler/loaders, you may run 'cobbler get-loaders' to download
        them, or, if you only want to handle x86/x86_64 netbooting, you may ensure that you have installed a *recent*
        version of the syslinux package installed and can ignore this message entirely.  Files in this directory,
        should you want to support all architectures, should include pxelinux.0, menu.c32, elilo.efi, and yaboot.
        The 'cobbler get-loaders' command is the easiest way to resolve these requirements.
    3 : enable and start rsyncd.service with systemctl
    4 : debmirror package is not installed, it will be required to manage debian deployments and repositories
    5 : The default password used by the sample templates for newly installed machines (default_password_crypted in
        /etc/cobbler/settings) is still set to 'cobbler' and should be changed, try: "openssl passwd -1 -salt
        'random-phrase-here' 'your-password-here'" to generate new one
    6 : fencing tools were not found, and are required to use the (optional) power management features. install cman or
        fence-agents to use them

    Restart cobblerd and then run 'cobbler sync' to apply changes.

How cool is that.

For 1.  `/etc/xinetd.d/tftp` :

    service tftp
    {
            socket_type             = dgram
            protocol                = udp
            wait                    = yes
            user                    = root
            server                  = /usr/sbin/in.tftpd
            server_args             = -s /var/lib/tftpboot
            disable                 = no
            per_source              = 11
            cps                     = 100 2
            flags                   = IPv4
    }

For 2.  Why not:

    sudo cobbler get-loaders

For 3.

    sudo systemctl enable rsyncd
    sudo systemctl start rsyncd

For 4.  turns out debmirror is not available for Centos7  https://github.com/cobbler/cobbler/issues/1396
For 5.  I like the default password I can look it up when I forget.
For 6.  Power Management is interesting .  https://fedorahosted.org/cobbler/wiki/PowerManagement  Further..
cman is cluster manager and has pacemaker in it. https://www.centos.org/docs/5/html/5.4/Technical_Notes/cman.html

I'll leave that off so that when I run cobbler check it will remind me again.  I don't think i can use it in my
current set up but.. interesting.

    sudo systemctl stop cobblerd
    sudo systemctl status cobblerd
    sudo systemctl start cobblerd
    sudo systemctl status cobblerd


and finally:

    cobbler sync

Which outputs

    task started: 2016-02-27_184004_sync
    task started (id=Sync, time=Sat Feb 27 18:40:04 2016)
    running pre-sync triggers
    cleaning trees
    removing: /var/lib/tftpboot/grub/images
    copying bootloaders
    trying hardlink /var/lib/cobbler/loaders/pxelinux.0 -> /var/lib/tftpboot/pxelinux.0
    trying hardlink /var/lib/cobbler/loaders/menu.c32 -> /var/lib/tftpboot/menu.c32
    trying hardlink /var/lib/cobbler/loaders/yaboot -> /var/lib/tftpboot/yaboot
    trying hardlink /usr/share/syslinux/memdisk -> /var/lib/tftpboot/memdisk
    trying hardlink /var/lib/cobbler/loaders/grub-x86.efi -> /var/lib/tftpboot/grub/grub-x86.efi
    trying hardlink /var/lib/cobbler/loaders/grub-x86_64.efi -> /var/lib/tftpboot/grub/grub-x86_64.efi
    copying distros to tftpboot
    copying images
    generating PXE configuration files
    generating PXE menu structure
    rendering DHCP files
    rendering DNS files
    rendering TFTPD files
    generating /etc/xinetd.d/tftp
    cleaning link caches
    running post-sync triggers
    running python triggers from /var/lib/cobbler/triggers/sync/post/*
    running python trigger cobbler.modules.sync_post_restart_services
    running: service dnsmasq restart
    received on stdout:
    received on stderr: Redirecting to /bin/systemctl restart  dnsmasq.service

    running shell triggers from /var/lib/cobbler/triggers/sync/post/*
    running python triggers from /var/lib/cobbler/triggers/change/*
    running python trigger cobbler.modules.scm_track
    running shell triggers from /var/lib/cobbler/triggers/change/*
    *** TASK COMPLETE ***

And then it asked to enable and start xinetd.. which turned out to not be installed.


    sudo yum install xinetd
    sudo systemctl enable xinetd
    sudo systemctl start xinetd
    sudo systemctl status xinetd


## Load in a Distro

The Olindata page talks about getting a distro CD.  It would be nice to be able to point at the right web based directory
to do the upload.

What I did was create a thumb drive by grabbing the most recent minimal centos7 from centos.org and then following
these instructions on creating the thumb drive. http://www.ubuntu.com/download/desktop/create-a-usb-stick-on-mac-osx

    hdiutil convert -format UDRW -o CentOS-7-x86_64-Minimal-1511.img CentOS-7-x86_64-Minimal-1511.iso
    diskutil list
    diskutil unmountDisk /dev/disk2
    sudo dd if=CentOS-7-x86_64-Minimal-1511.img.dmg  of=/dev/rdisk2 bs=1m
    diskutil eject /dev/disk2

As soon as I finished creating this I discovered that I can skip the thumbdrive all together and simply loop mount the
iso.  https://en.wikipedia.org/wiki/Loop_device

    mount CentOS-7-x86_64-Minimal-1511.iso /media/centos7min1511 -o loop

This treats the file as a device.  Iso files are properly formated to be a device.

On the cobbler machine. I stuck the usb stick into the machine and found that it was /dev/sdb1 with

    fdisk -l

    mkdir /media/usb
    mount /dev/sdb1 /media/usb

    cobbler import --arch=x86_64 --path=/media/usb --name=Centos-7-1511

So I loaded that and didn't like the name. Here is an interesting article with how to move around names and such.
http://blog.delouw.ch/2011/02/28/updating-a-distro-in-cobbler/

    cobbler profile remove --name=Centos-7-1511-x86_64
    cobbler distro remove --name=Centos-7-1511-x86_64
    cobbler import --arch=x86_64 --path=/media/usb --name=CentOS-7-1511

And the output:

    task started: 2016-02-28_190411_import
    task started (id=Media import, time=Sun Feb 28 19:04:11 2016)
    Found a candidate signature: breed=redhat, version=rhel6
    Found a candidate signature: breed=redhat, version=rhel7
    Found a matching signature: breed=redhat, version=rhel7
    Adding distros from path /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64:
    creating new distro: CentOS-7-1511-x86_64
    trying symlink: /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64 -> /var/www/cobbler/links/CentOS-7-1511-x86_64
    creating new profile: CentOS-7-1511-x86_64
    associating repos
    checking for rsync repo(s)
    checking for rhn repo(s)
    checking for yum repo(s)
    starting descent into /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64 for CentOS-7-1511-x86_64
    processing repo at : /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64
    need to process repo/comps: /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64
    looking for /var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64/repodata/*comps*.xml
    Keeping repodata as-is :/var/www/cobbler/ks_mirror/CentOS-7-1511-x86_64/repodata
    *** TASK COMPLETE ***

List out whats in.

    cobbler list

    cobbler distro report --name=CentOS-7-1511-x86_64

    cobbler sync

I went ahead and added OlinData's kickstart file as `/var/lib/cobbler/kickstarts/CentOS-7.ks`  Editing to match
my IPs and Distro names.

    cobbler profile edit --name=CentOS-7-1511-x86_64 --kickstart=/var/lib/cobbler/kickstarts/CentOS-7.ks


## Adding A System


    cobbler system add --name=resource01 --profile=CentOS-7-1511-x86_64  \
          --interface=enp0s25 --mac=b8:ae:ed:78:a1:14  --ip-address=172.16.222.11 --netboot-enabled=1 --static=1

    cobbler system list
    cobbler system report --name=resource01

    cobbler sync

At this point I put a keyboard and screen on the target machine and rebooted, On this machnine F10 put me into Bios
 mode where I picked the LAN as my Boot device.

It loaded right up.

btw.. the root password is the same as the default for cobbler.  You can change that with the instructions from
`/etc/cobbler/settings`

    # The simplest way to change the password is to run
    # openssl passwd -1
    # and put the output between the "" below.
    default_password_crypted: "$1$mF86/UHC$WvcIcX2t6crBz2onWxyac."


What I discovered is that the IP was not set to what I was expecting. I decided that becasue /etc/hosts had an entry
for the IP I wanted to give it, it was thinking that the IP was already taken.  So I removed it from /etc/hosts and fixed
the nameservers to point locally. Then rebooted the system.

When it came back up I could ping resource02 but not resource01 but when i did a dig of resource02 I noticed that
dig was going to 8.8.8.8 and not resolving resource02 (which was in my /etc/hosts file that should be loaded by dnsmasq)

Further `netstat -tulpn`  showed that nothing was listening on port 53. finally `systemctl status dnsmasq` showed it was
dead.

Before I enabled and started it I wanted to make sure it was not started up automatically by anything in cobbler.   So
I re PXE booted the resource01 computer and it in fact was not able to PXEBoot.

    sudo systemctl start dnsmasq
    sudo systemctl enable dnsmasq

Rebuilt it again and it comes back 172.16.222.10 again.    You can find the dhcp leases in `/var/lib/NetworkManager` on
the client machine.  Mine was:

    lease {
      interface "enp0s25";
      fixed-address 172.16.222.10;
      filename "pxelinux.0";
      option subnet-mask 255.255.255.0;
      option routers 172.16.222.14;
      option dhcp-lease-time 3600;
      option dhcp-message-type 5;
      option domain-name-servers 172.16.222.14;
      option dhcp-server-identifier 172.16.222.14;
      option dhcp-renewal-time 1800;
      option broadcast-address 172.16.222.255;
      option dhcp-rebinding-time 3150;
      renew 1 2016/02/29 08:43:28;
      rebind 1 2016/02/29 09:08:26;
      expire 1 2016/02/29 09:15:56;
    }

So the lease was correct and it was coming from the right server.

Looking at cobbler `cobbler system report --name=resource01`

    Name                           : resource01
    TFTP Boot Files                : {}
    Comment                        :
    Enable gPXE?                   : <<inherit>>
    Fetchable Files                : {}
    Gateway                        :
    Hostname                       :
    Image                          :
    IPv6 Autoconfiguration         : False
    IPv6 Default Device            :
    Kernel Options                 : {}
    Kernel Options (Post Install)  : {}
    Kickstart                      : <<inherit>>
    Kickstart Metadata             : {}
    LDAP Enabled                   : False
    LDAP Management Type           : authconfig
    Management Classes             : <<inherit>>
    Management Parameters          : <<inherit>>
    Monit Enabled                  : False
    Name Servers                   : []
    Name Servers Search Path       : []
    Netboot Enabled                : True
    Owners                         : <<inherit>>
    Power Management Address       :
    Power Management ID            :
    Power Management Password      :
    Power Management Type          : ipmitool
    Power Management Username      :
    Profile                        : CentOS-7-1511-x86_64
    Internal proxy                 : <<inherit>>
    Red Hat Management Key         : <<inherit>>
    Red Hat Management Server      : <<inherit>>
    Repos Enabled                  : False
    Server Override                : <<inherit>>
    Status                         : production
    Template Files                 : {}
    Virt Auto Boot                 : <<inherit>>
    Virt CPUs                      : <<inherit>>
    Virt Disk Driver Type          : <<inherit>>
    Virt File Size(GB)             : <<inherit>>
    Virt Path                      : <<inherit>>
    Virt PXE Boot                  : 0
    Virt RAM (MB)                  : <<inherit>>
    Virt Type                      : <<inherit>>
    Interface =====                : enp0s25
    Bonding Opts                   :
    Bridge Opts                    :
    CNAMES                         : []
    InfiniBand Connected Mode      : False
    DHCP Tag                       :
    DNS Name                       :
    Per-Interface Gateway          :
    Master Interface               :
    Interface Type                 :
    IP Address                     : 172.16.222.11
    IPv6 Address                   :
    IPv6 Default Gateway           :
    IPv6 MTU                       :
    IPv6 Prefix                    :
    IPv6 Secondaries               : []
    IPv6 Static Routes             : []
    MAC Address                    : b8:ae:ed:78:52:9b
    Management Interface           : False
    MTU                            :
    Subnet Mask                    :
    Static                         : True
    Static Routes                  : []
    Virt Bridge                    :

This was correct for the ip and the interface, and the MAC Address.

So what about dnsmasq configuration?

    # Cobbler generated configuration file for dnsmasq
    # Mon Feb 29 01:23:54 2016

    # resolve.conf .. ?
    #no-poll
    #enable-dbus
    read-ethers
    addn-hosts = /var/lib/cobbler/cobbler_hosts

    dhcp-range=172.16.222.6,172.16.222.99
    dhcp-option=3,172.16.222.14
    dhcp-lease-max=1000
    dhcp-authoritative
    dhcp-boot=pxelinux.0
    dhcp-boot=net:normalarch,pxelinux.0
    dhcp-boot=net:ia64,/var/lib/cobbler/elilo-3.6-ia64.efi

    dhcp-host=net:x86_64,b8:ae:ed:78:52:9b,172.16.222.11

Note that that is also correct for 172.16.222.11

All I can think to do is build out another computer.


    cobbler system add --name=resource03 --profile=CentOS-7-1511-x86_64
    --interface=enp0s25 --mac=b8:ae:ed:78:9a:71  --ip-address=172.16.222.13 --netboot-enabled=1 --static=1

it came up with the wrong ip.  But then I looked at the dnsmasq configuration and it didn't have an entry for `172.16.222.13`.
I realized i had not done cobbler sync.

    cobbler sync

At this point redoing the system worked.

But trying resource01 again did not work.  I went in and edited the dhclient file in `/var/lib/NetworkManager` and edited
the 172.16.222.10 to 172.16.222.11.  On reboot I found that that lease was tehre but a whole new section was created with
the 172.16.222.10 lease as well.  This means it is being saved on the dnsmasq server.

On the cobbler dnsmasq server there is a lease file in `/var/lib/dnsmasq/dnsmasq.leases`

    1456728260 b8:ae:ed:78:9a:71 172.16.222.13 * *
    1456729112 b8:ae:ed:78:a1:14 172.16.222.10 * *

The prescribed way to get rid of that lease is.

    systemctl stop dnsmasq

edit the file and remove the lease.

    systemctl start dnsmasq

I went ahead on the client machine and removed the lease file in /var/lib/NetworkManager  and then rebooted the client.

Then finally.. I realized that the mac address was wrong.. it was the mac address of the cobbler machine.  DOH!


cobbler system remove did not remove the entry from dnsmasq.conf so I did that myself.  Then added resource01 and then
`cobbler sync`

