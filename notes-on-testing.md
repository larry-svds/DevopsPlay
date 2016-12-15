# Testing Infrastructure

The `--check`, `--diff`, and `--limit`

if you run ansible it runs it but doesn't actually do it.. it shows what it would have done.

If you add --diff it shows what would change.. like file contents.  

if you add --limit you -limit it to a single system.

    ansible-playbook foo.yml --check --diff --limit foo.example.com

## Gauge-Ansible-Steps

GetGauge.io is a Specification based, open source, light weight, test automation
tool from  ThoughtWorks.  

You write your specifications in Markdown. Specs are run in Java, Ruby and C#.  

This is for acceptance testing, Business level integration tests.

It has close integration with Selenium, also from ThoughtWorks.  

I'd like to build a series of Guage that work use ansible.

Whats involved is a java driver program that simply calls out to ansible.  
