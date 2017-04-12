This directory is for a testing monitoring system for distributed data
processing systems.

The basic idea is.. capture the output of various commonly available
linux performance programs and convert to json and feed to Splunk
for further processing.

vmstat -n -t 5 | python vmstat-json.py | nc -w 1 -u prodpmsplunk1 8711

