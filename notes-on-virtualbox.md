# Virtual Box notes

Cool place to get virtual boxes.  osboxes.org

To expland them you will need 7zip http://superuser.com/questions/548349/how-can-i-install-7zip-so-i-can-run-it-from-terminal-on-os-x

    brew isntall p7zip
    7z x heed.7z

## Bridged Networks

Configure it like you would the host itself. IE.  I was able to use my bare-metal mantl instructions to
give my bridged centos VM a static IP

https://github.com/CiscoCloud/mantl/blob/master/docs/getting_started/bare-metal.rst


## Vagrant

This too.  http://www.vagrantbox.es/

Note that you have to preload the boxes before you can use them in your
vagrant file.

    vagrant box add {title} {url}

