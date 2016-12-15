# Notes on generating a the terraform/ansible system.

This project came about when trying to get push button down to a push of a button.

There are a variety of issues with creating a seemless ansible and terraform:

* Two Systems
    * variables in one are needed in the other, but we want only have input location.
      For example the ssh key.
    * generation of the terraform, changes values needed for the other. For example
      the ip of the bastion host.
* Terraform
    * purely immutable json definition does not have conditionals or loop structures.
    * We want to be able to chose a type of instance for a host group that might
      require different terraform resources.
* Ansible
    * Shared variables and changed values affect ansible as the downstream system.
    * Would like to define the roles to run on hosts and facets where we define those
      instead of at