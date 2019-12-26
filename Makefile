.PHONY: all check apply install-deps

ansible-playbook=ansible-playbook -i hosts.yml playbook.yml

all: check

install-deps:
	ansible-galaxy install -r requirements.yml

check: install-deps
	$(ansible-playbook) --check --diff

apply: install-deps
	$(ansible-playbook) --diff
