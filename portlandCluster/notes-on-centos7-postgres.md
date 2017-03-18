# Postgres on Centos7

I need to get a postgres database on Control01 for airflow and
other needs within the cluster.   Sophia for one.  

I am not a fan of databases in docker.  Not without host mounted data
directories on something like ceph. and the container running in a mesos, behind a VIP. Then its a little slow.. 
but actually ha-ish and pretty cool :)

 
### Install packages

The [postgresql official page](https://wiki.postgresql.org/wiki/YUM_Installation) 
suggests turning off getting postgres from the standard repos.  This seems 
a bit extreme for my purposes.  I'd rather just use the version that has been testes with 
centos.

After comparing a few install blogs, [this one](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7) 
works for me. 


    $ sudo yum install postgresql-server postgresql-contrib
    $ sudo postgresql-setup initdb
    Initializing database ... Full path required for exclude: net:[4026532251].
    Full path required for exclude: net:[4026532251].
    Full path required for exclude: net:[4026532251].
    OK

### Allow password logins    
    
Fix postgres to allow user name and password authentication instead of insisting on
linux system accounts as logins. 
    
    $ sudo vi /var/lib/pgsql/data/pg_hba.conf
    
Change:

    host    all             all             127.0.0.1/32            ident
    host    all             all             ::1/128                 ident
    
to:

    host    all             all             127.0.0.1/32            md5
    host    all             all             ::1/128                 md5
    
Start and enable service:

    $ sudo systemctl start postgresql
    $ sudo systemctl enable postgresql
  
Unfortunately there is one more thing you have to do for this file.  Check the 
"letting external IPs hit your Server" for more that has to be done in `pg_hba.conf`
    
### letting external IPs hit your Server
    
THis was a bit harder to find.. 

    sudo su -
    cd /var/lib/pgsql/data/
    vi posgresql.conf
    
    #------------------------------------------------------------------------------
    # CONNECTIONS AND AUTHENTICATION
    #------------------------------------------------------------------------------
    
    # - Connection Settings -
    
    #listen_addresses = 'localhost'         # what IP address(es) to listen on;
                                            # comma-separated list of addresses;
                                            # defaults to 'localhost'; use '*' for all
                                            # (change requires restart)
    #port = 5432                            # (change requires restart)

and change it by uncommenting the listen_addresses line and changing localhost to *. Like this:
    
    # - Connection Settings -
    
    listen_addresses = '*'                  # what IP address(es) to listen on;
                                            # comma-separated list of addresses;
                                            # defaults to 'localhost'; use '*' for all
                                            # (change requires restart)
    #port = 5432                            # (change requires restart)
    
once you save that.  restart service
    
But that wasn't enough.. turns out.. when I tried this I get.. 
    
    $ psql -U philo -d sophia -h control01
    psql: FATAL:  no pg_hba.conf entry for host 
            "172.16.222.231", user "philo", database "sophia", SSL off

So it was restricting the network that i could be calling from.  This setting is in 
`/var/lib/pgsql/data/pg_hba.conf` We already changed this line to accept md5s.. now 

    host    all             all             127.0.0.1/32            md5

Needs to open up to other boxes.. Since we are opening this database up to password logins
we can change make this restricted to IPs in my local network. 

    host    all             all             172.16.222.1/24            md5

And then restart the services with `systemctl stop postgresql` and `start`.
    
    
    
### Create Sophia and Philo    

At this point if you did :

    $psql
    psql: FATAL:  role "centos" does not exist

So switch to the postgres user that got created in the yum install.

    $ sudo -i -u postgres
    $ psql
    # \q
    
    $ createuser --interactive 
    Enter name of role to add: philo
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n
    createdb sophia

Or inside the db do:

    create user philo with password '<somethinghard>';
    create database sophia;

Give philo privs on database AND Schema.     
    
    # grant all privileges on database sophia to philo;
    # alter user philo with password '<somethinghard>';
    # \c sophia
    sophia=# grant all privileges on all tables in schema public to philo;
    sophia=# grant all privileges on all sequences in schema public to philo;

I then copied the contents of the file  `sophia/metadata_db/sql/create_metadata_tables.sql`
into `~/sophia_create_tables.sql`
    
    # \i sophia_create_tables.sql 
    psql:sophia_create_tables.sql:12: NOTICE:  CREATE TABLE will create implicit sequence "model_id_seq" for serial column "model.id"
    psql:sophia_create_tables.sql:12: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "model_pkey" for table "model"
    CREATE TABLE
    psql:sophia_create_tables.sql:23: NOTICE:  CREATE TABLE will create implicit sequence "model_version_id_seq" for serial column "model_version.id"
    psql:sophia_create_tables.sql:23: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "model_version_pkey" for table "model_version"
    CREATE TABLE
    psql:sophia_create_tables.sql:32: NOTICE:  CREATE TABLE will create implicit sequence "component_mapping_id_seq" for serial column "component_mapping.id"
    psql:sophia_create_tables.sql:32: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "component_mapping_pkey" for table "component_mapping"
    CREATE TABLE
    psql:sophia_create_tables.sql:47: NOTICE:  CREATE TABLE will create implicit sequence "asset_id_seq" for serial column "asset.id"
    psql:sophia_create_tables.sql:47: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "asset_pkey" for table "asset"
    CREATE TABLE
    psql:sophia_create_tables.sql:58: NOTICE:  CREATE TABLE will create implicit sequence "data_id_seq" for serial column "data.id"
    psql:sophia_create_tables.sql:58: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "data_pkey" for table "data"
    CREATE TABLE
    psql:sophia_create_tables.sql:74: NOTICE:  CREATE TABLE will create implicit sequence "trained_model_id_seq" for serial column "trained_model.id"
    psql:sophia_create_tables.sql:74: NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "trained_model_pkey" for table "trained_model"
    CREATE TABLE
    postgres=#
    
Look at the tables.     

    postgres=# \d
    
So they went into postgres.. grr.  Change database. 

    postgres=# \c sophia
    sophia=# \i sophia_create_tables.sql

    

    