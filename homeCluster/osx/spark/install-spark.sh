#!/usr/bin/env bash
ansible-playbook -u centos -i ../microservices-infrastructure/inventory --ask-sudo-pass   install-spark.yml >& install-spark.log
