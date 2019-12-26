#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: oxs_pmset

short_description: Manage power management configuration exposed by pmset

description: >
  Allows changing power management settings by invoking `pmset`. Configuration
  dicts `on_battery` and `on_charger` can have any key present in the output 
  of `pmset -g custom`.

options:
    on_battery:
        description: settings on battery power
    on_charger:
        description: settings when connected to power adapter
'''

EXAMPLES = r''' # '''

from ansible.module_utils.basic import AnsibleModule


def parse_pmset_output(output):
    """Parses `pmset -g custom` into a 2-level dict."""
    r = {}
    for line in output.split('\n'):
        if line == '':
            continue
        if line[0] != ' ' and line[-1] == ':':
            section_name = line[:-1]
            r[section_name] = {}
        else:
            k, v = line.split()
            r[section_name][k] = v
    return r


def run_module():
    module_args = dict(
        on_battery=dict(type='dict', required=False, default=dict()),
        on_charger=dict(type='dict', required=False, default=dict()),
    )
    result = dict(changed=False, diff=dict(before='', after=''))
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    _, stdout, _ = module.run_command(["pmset", "-g", "custom"], check_rc=True)

    commands = []
    output = parse_pmset_output(stdout)
    def add_diff(block, param, old_value, new_value):
        result['diff']['before'] += '{block}.{param}={val}\n'.format(
            block=block, param=param, val=old_value)
        result['diff']['after'] += '{block}.{param}={val}\n'.format(
            block=block, param=param, val=new_value)        

    blocks = [
        ('on_battery', '-b', output['Battery Power']),
        ('on_charger', '-c', output['AC Power']),
    ]
    for block, mode_flag, current_values in blocks:
        # Iterate over user-specified parameters and check if there's anything
        # to change.
        for param, value in module.params[block].items():
            if value is None: continue
            if param not in current_values:
                module.fail_json(msg=(
                    '{} is not present in pmset output. Run '
                    '`pmset -g custom` to see the list of valid parameters'
                ).format(param),
                                 **result)
            orig = current_values[param]
            if isinstance(value, int):
                orig = int(orig)
            if orig != value:
                add_diff(block, param, orig, value)
                commands.append(['pmset', mode_flag, param, value])

    if commands:
        result['changed'] = True
    if module.check_mode:
        module.exit_json(**result)

    for command in commands:
        # Explicitly convert all arguments to strings, so that
        # module.run_command doesn't choke on ints.
        cmd = [str(v) for v in command]
        module.run_command(cmd, check_rc=True)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
