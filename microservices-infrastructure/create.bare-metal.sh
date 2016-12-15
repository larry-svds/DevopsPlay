ansible-playbook -u centos -i inventory \
	--ask-sudo-pass \
        -e provider=bare-metal \
        -e consul_dc=dc1 \
        -e docker-lvm-backed=true \
        -e docker_lvm_data_volume_size="80%FREE" \
        -e @security.yml  sample.yml >& bare-metal.log
