#Notes on Installing Spark on the workers

This is from https://github.com/booz-allen-hamilton/ansible-role-spark-library

I am going to install this without hadoop so that I configure it later. This allows
you more freedom. iN fact this is the case where you are providing the hadoop.
More instructions here: http://spark.apache.org/docs/latest/hadoop-provided.html

This package from booz-allen was built for spark 1.5.2. and hadoop2.6

I am going to use spark `1.6.1` and type `without-hadoop`  you end this in
`roles/spark/vars/main.yml`

The info is here :  http://www.apache.org/dist/spark/spark-1.6.1/

By checking out http://www.apache.org/dist/spark/spark-1.5.2/spark-1.5.2-bin-hadoop2.6.tgz.sha
I figured out how to modify the sha line in `roles/spark/vars/main.yml`.

Set install-spark.sh to an executable, it has all the needed command line parameters.  To watch along
as you run ./install-spark.sh, open another shell and `tail -f install-shell.log`

I also created run.sh to do something much more local without reference to the cluster. 

I had ot change it to 1.6.2 because in Oct 2016 1.6.1 was not available there. 