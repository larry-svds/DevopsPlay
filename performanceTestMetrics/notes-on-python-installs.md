# fun with python

### Install with out root privs

#### getting a local pip.

    wget -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --user

This puts pip in `~/.local/bin`  add this path to your path in `.bashrc`

    PATH=$PATH:~/.local/bin

Its a good idea to make sure `~/.local` is only writable by you. Source it to make it take effect in
your current path:

    source ~/.bashrc

Then you can install things like:

    pip install --user fabric

only I got a ton of errors about trying to run gcc on the machine. So for this at least..

    python
    >>> from fabric.api import run
    Traceback ...
    ImportError: No module named fabric.api

I'll leave this hear incase I find next steps.


