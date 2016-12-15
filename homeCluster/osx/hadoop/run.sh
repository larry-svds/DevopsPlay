#!/usr/bin/env bash

ansible-playbook -u larry -K -i inventory install-client.yml
