# DC/OS Kafka

I added the Confluent Kafka package from the Universe Selected Packages. 

When you install it you can dowload a pdf. Which I [have locally at](file:///Users/larry/Documents/Confluent_Mesosphere_Whitepaper.pdf)

When I made room for kafka it completed but the "open service" button brought up a "page can't be found"
for `http://172.16.222.7/service/confluent-kafka/` (.7 is the master node) This same pattern does 
work for Zepplin.  

No errors seemed to be reported.   I logged into the machine with a broker and the "confluent-kafka"
tasand went looking for logs. 


### Going through [the confluent mesosphere whitepaper](file:///Users/larry/Documents/Confluent_Mesosphere_Whitepaper.pdf)

    dcos package install --cli kafka
    
   