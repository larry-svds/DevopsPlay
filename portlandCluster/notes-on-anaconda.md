# Notes on Anaconda

## Install

Anaconda is kinda set up to be installed by users.  Rather than think about it,
I'll do that too. In a browser got the url for the
right installer, I chose Python 3.6.

    ssh centos@control01
    curl -O https://repo.continuum.io/archive/Anaconda3-4.3.0-Linux-x86_64.sh
    bash Anaconda3-4.3.0-Linux-x86_64.sh

So promising..

        Anaconda3 will now be installed into this location:
    /home/centos/anaconda3

      - Press ENTER to confirm the location
      - Press CTRL-C to abort the installation
      - Or specify a different location below

    [/home/centos/anaconda3] >>>
    PREFIX=/home/centos/anaconda3
    tar (child): bzip2: Cannot exec: No such file or directory
    tar (child): Error is not recoverable: exiting now
    tar: Child returned status 2
    tar: Error is not recoverable: exiting now

So

    sudo yum install -y bzip2
    bash Anaconda3-4.3.0-Linux-x86_64.sh

    [/home/centos/anaconda3] >>>
    ERROR: File or directory already exists: /home/centos/anaconda3

Doh!

    rm -rf anaconda3
    bash Anaconda3-4.3.0-Linux-x86_64.sh

After a ton of installs, it asks if  want to add anaconda to the
front of my path.

    creating default environment...
    installation finished.
    Do you wish the installer to prepend the Anaconda3 install location
    to PATH in your /home/centos/.bashrc ? [yes|no]
    [no] >>> yes

source your .bashrc to prepend anaconda to your path in your current shell.

    source .bashrc

## Requirements for Sophia Execution Env

    pip install zip
    pip install gitpython

When I ran airflow though I got an error because airflow is using the syste
python 2.7.  So.. to install those two for that environment..

    [centos@control01 ~]$ echo $PATH
    /home/centos/anaconda3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/centos/.local/bin:/home/centos/bin
    [centos@control01 ~]$ export PATH="/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/centos/.local/bin:/home/centos/bin"
    [centos@control01 ~]$ echo $PATH
    /usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/centos/.local/bin:/home/centos/bin

    sudo pip install zip
    sudo pip install gitpython
    sudo pip install pyyaml


    source .bashrc

Then run the webserver

    airflow webserver -p 8080


## Running a Jupyter notebook

    jupyter notebook

will bring up the notebook UI. When you open a notebook it might complain that
it needs a python2 kernel and ask you to pic a kernel or continue without a
kernel.   [To get python2 kernel added.](http://ipython.readthedocs.io/en/stable/install/kernel_install.html)


    jupyter kernelspec list
    python2 -m pip install ipykernel
    python2 -m ipykernel install --user
    jupyter kernelspec list


Thing is, it then needed a bunch of things in that environment. So I wanted to use the
other way way described using conda.

    conda create -n ipykernel_py2 python=2 ipykernel
    source activate ipykernel_py2
    python -m ipykernel install --user

Whats interesting is if I do a `jupyter kernelspec list` while
ipykernel_py2 is activated all I see is the one python2 kernel.
Once I deactivate I can see 3 and 2 with `jupyter kernelspec list`.

    pip install matplotlib
    pip install scipy
    pip install sklearn
    pip install pandas

To install locally

    pip install -e /Users/larry/src/sophia/tryjupyter/sophia/interface

I tried at some of the sub directory levels but it is looking for `setup.py`
When I ran the notebook.. another was needed.

    pip install pyyaml


