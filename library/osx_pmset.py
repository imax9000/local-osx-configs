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

options:
    on_battery: settings on battery power
    on_charger: settings when connected to power adapter
'''

EXAMPLES = r''' # '''

from ansible.module_utils.basic import AnsibleModule

def parse_pmset_output(output):
    r = {}
    for line in output.split('\n'):
        if line == '':
            continue
        if line[0] != ' '  and line[-1] == ':':
            section_name = line[:-1]
            r[section_name] = {}
        else:
            k,v = line.split()
            r[section_name][k] = v
    return r


def run_module():
    on_battery_params = dict(
        str_params=['hibernatefile'],
        int_params=['acwake', 'disksleep', 'displaysleep', 'gpuswitch',
                    'halfdim','hibernatemode', 'highstandbythreshold', 
                    'lessbright', 'lidwake', 'powernap', 'proximitywake',
                    'sleep', 'standby', 'standbydelayhigh', 'standbydelaylow',
                    'tcpkeepalive', 'ttyskeepawake']
        )
    on_charger_params = dict(
        str_params=['hibernatefile'],
        int_params=['acwake', 'disksleep', 'displaysleep', 'gpuswitch',
                    'halfdim', 'hibernatemode', 'highstandbythreshold',
                    'lidwake', 'networkoversleep', 'powernap', 'proximitywake',
                    'sleep', 'standby', 'standbydelayhigh', 'standbydelaylow',
                    'tcpkeepalive', 'ttyskeepawake', 'womp'],
        )
    def make_params(desc):    
        params = dict()
        params.update({param: dict(type='str', required=False)
                        for param in desc['str_params']})
        params.update({param: dict(type='int', required=False)
                        for param in desc['int_params']})
        return dict(
            type='dict',
            required=False,
            default=dict(),
            options=params,
        )

    module_args = dict(
        on_battery=make_params(on_battery_params),
        on_charger=make_params(on_charger_params),
    )
    result = dict(
        changed=False,
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    exitcode, stdout, stderr = module.run_command(["pmset", "-g", "custom"])
    if exitcode != 0:
        module.fail_json(
            msg='pmset returned non-zero exit code',
            exitcode=exitcode,
            stderr=stderr,
            **result)

    result['diff'] = dict(before='', after='')

    changes = []
    output = parse_pmset_output(stdout)
    on_battery = output['Battery Power']
    on_charger = output['AC Power']
    for k,v in module.params['on_battery'].items():
        if v is None: continue
        orig = on_battery[k]
        if isinstance(v, int):
            orig = int(orig)
        if orig != v:
            result['changed'] = True
            result['diff']['before'] += '{block}.{param}={val}\n'.format(block='on_battery',param=k,val=orig)
            result['diff']['after'] += '{block}.{param}={val}\n'.format(block='on_battery',param=k,val=v)
            changes.append(['-b', k, v])
    for k,v in module.params['on_charger'].items():
        if v is None: continue
        orig = on_charger[k]
        if isinstance(v, int):
            orig = int(orig)
        if orig != v:
            result['changed'] = True
            result['diff']['before'] += '{block}.{param}={val}\n'.format(block='on_charger',param=k,val=orig)
            result['diff']['after'] += '{block}.{param}={val}\n'.format(block='on_charger',param=k,val=v)
            changes.append(['-c', k, v])

    if module.check_mode:
        module.exit_json(**result)

    for change in changes:
        cmd = ["pmset"] + [str(v) for v in change]
        print("Running: {}".format(" ".join(cmd)))
        module.run_command(cmd, check_rc=True)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
