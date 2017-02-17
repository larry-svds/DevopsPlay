#!/usr/bin/env bash
# This only works with virtual box VMs because they
# use this device name 'enp0s3'
# and now using for my nuc's which use enp0s25
set -o nounset -o errexit
export PATH=/usr/sbin:/usr/bin:$PATH
echo $(ip addr show enp0s25 | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)

