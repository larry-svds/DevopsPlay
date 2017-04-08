# Fabric - Python ssh

I was on control01 whcih has anaconda3 on it.

    pip instal fabric

oops it says it needs to be on python 2.5-2.7

    conda info --envs

just showed my anaconda3.  I looked at the pythons that were available with

    conda search python

which showed me a lot of stuffs..   I did see 2.7.13.   So creating an
environment for me to call out on fabric.. I am calling my whole cobbled
together execution environment `trogdor` so:

    conda create --name trogdor python=2.7.13

to use this you do `source activate trogdor` and `source deactivate trogdor`

to list the packages installed `conda list -n trogdor`. More conda package
info at https://conda.io/docs/using/pkgs.html

Finally the `conda` way to install the package:

    conda install -n trogdor fabric

and here is my `fabfile.py` that demos the commands I need.

    from fabric.api import local, run, cd, env, put

    env.hosts = ['lmurdock@172.16.222.4']

    def hello(name="bob"):
        print("Hello %s! " % name)
        local('python --version')
        run('python --version')
        run('mkdir -p tryfabric')
        with cd('tryfabric'):
            run('mkdir -p bob')
            put('myfile.py','myfile.py')

 this is called with:

    fab hello:name=larry

##### Calling building remote executor

 * with server, language, model, ver, 'environment.yml', asset_info

fabric file logic is:

    if <language>.lower = 'python'

        env.hosts = [<server>]
        run(mkdir -p <model>)
        run(mkdir -p <model>/<ver>)
        put(<requirements.txt>, <model>/<ver>/environment.yml)

        env_name = '<model>_<ver>'
        run('if conda info --envs | grep <env_name> ; then echo "using conda <env_name>" ;
            else conda env create --name    --file environment.yml; fi')
;
        put( <asset_info.file_name>, <model>/<ver>/<asset_info.file_name>)
        for any file dependencies in <asset_info>
           get _dep_asset_info from modelversion
           put( <dep_asset_info.file_name>, <model>/<ver>/<dep_asset_info.file_name>)


now for the run_phase.py file:

    Create input and output paths.

    call the function with parameters

Add this to the fabric file

    put( 'run_phase.py', <model>/<ver>/run_phase.py)


And then finally the actual run.

    run('cd <model>/<ver> ; source activate <env_name>; python run_phase.py')

with
