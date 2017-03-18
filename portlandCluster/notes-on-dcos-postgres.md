# Notes on DCOS Postgres

Installing Postgres and Postgres admin from Universe on DCOS. 

I already created a nfs mount on `/mnt/nfs` on all slaves and we will use that for storage.  What it lacks in speed
it at least will be resilient. 

## Install 

I did the advanced install of Postgresql 9.6-0.2

 * Postgresql tab
   * Mem: 2048 -- There is lots of memory on these systems. 
 * Database tab. 
   * password: dead
 * Storage tab
   * pdata: /var/lib/postgresql/data
 * networking tab
   * turned on host mode so I can check the database knowing 
      the current location.  You don't want more than one postgres
      on these tiny nodes anyways. 
   * enable external access : checked -- uses port 15432
   
What is weird is that when it was done, it did not use 15432. Instead it used 5432.  Probably becuase 
I used Host networking.  They way I figured that out is by looking at the logs of the `marathon_lb` 
service. But also you can peek behind the scenes and see for sure what is exactly going on with: 

    172.16.222.8:9090/haproxy?stats
        
You can log in remotely from say your laptop with 
    
    psql -h 172.16.222.8 -d defaultdb -U admin
    
Note that if you forget the database name and user, you just won't get in.  The error message is perfectly 
aweful.  

## Setup Sophia
    
I then set up sophia and philo per the section in [notes-on-centos7-postgres](notes-on-dcos-postgres.md)