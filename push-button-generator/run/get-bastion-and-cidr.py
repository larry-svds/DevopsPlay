#!/usr/bin/env python

import json

import sys

#file_path = '{}terraform.tfstate'.format(sys.argv[1])
file_path = 'terraform.tfstate'
print file_path

with open(file_path) as data_file:
    data = json.load(data_file)

for module in  data['modules']:
    if ( 'bastion'in module['path'] ):
        bastion_ip = module['outputs']['ec2_ips']
        print bastion_ip
    if ( 'vpc' in module['path'] ):
        cidr = module["resources"]["aws_vpc.main"]["primary"]["attributes"]["cidr_block"]
        print cidr
prefix = (cidr.split('/')[0]).split('.')
print prefix
bits = int(cidr.split('/')[1])
if bits < 24 :
    ip_mask = '{}.{}.*.*'.format(prefix[0],prefix[1])
else:
    ip_mask = '{}.{}.{}.*'.format(prefix[0],prefix[1],prefix[2])

print '{},{}'.format()