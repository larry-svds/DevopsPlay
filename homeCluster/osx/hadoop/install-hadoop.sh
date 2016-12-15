#!/usr/bin/env bash
ansible-playbook -u hadoop -i ../inventory --ask-sudo-pass   install-hadoop.yml >& install-hadoop.log
