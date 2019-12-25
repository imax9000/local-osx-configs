.PHONY: all check apply

ansible-playbook=ansible-playbook -i hosts.yml playbook.yml

all: check

check:
	$(ansible-playbook) --check --diff

apply:
	$(ansible-playbook) --diff
