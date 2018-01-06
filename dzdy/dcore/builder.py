import re
from dzdy.dcore import BlueprintCTBN, BlueprintCTMC

__author__ = 'TimeWz667'
__all__ = ['restore_dcore_from_json', 'restore_dcore_from_script']


def script_to_json(scr):
    dcs = scr.split('\n')
    while dcs:
        dc = dcs[0]
        pars = re.match(r'(?P<Type>CTBN|CTMC)\s+(?P<Name>\w+)\s*\{', dc, re.I)
        if pars:
            break
        else:
            dcs = dcs[1:]

    try:
        pars = pars.groupdict()
    except AttributeError:
        raise SyntaxError

    dcs = [re.sub(r'\s+', '', st) for st in dcs]
    dcs = [re.sub(r'#\w+', '', st) for st in dcs if st is not '']

    js = {'ModelName': pars['Name'], 'ModelType': pars['Type']}

    if pars['Type'] == 'CTBN':
        mss = [re.match(r'(?P<node>\w+)\[(?P<ms>(\w|\|)+)\]', st) for st in dcs]
        mss = {ms.group('node'): ms.group('ms').split('|') for ms in mss if ms}

        sts = [re.match(r'(?P<state>(\w|\|)+)\{(?P<ms>(.*)+)\}', st) for st in dcs]
        sts = {st.group('state'): dict(re.findall(r'(?P<a>\w+):(?P<b>\w+)', st.group('ms'))) for st in sts if st}
        targets = {st: list() for st in sts.keys()}
        js['Microstates'] = mss
        js['States'] = sts

    elif pars['Type'] == 'CTMC':
        sts = [re.match(r'(?P<state>\A(\w|\|)+\Z)', st) for st in dcs]
        sts = [st.group('state') for st in sts if st]
        targets = {st: list() for st in sts}

        js['States'] = sts

    else:
        raise SyntaxError('Can not specify model type')

    tr1 = [re.match(r'((\w|\|)+--)*(?P<fr>(\w|\|)+)\((?P<by>\w+)\)->(?P<to>(\w|\|)+)', st) for st in dcs]
    tr1 = {tr.group('fr'): {'Dist': tr.group('by'), 'To': tr.group('to')} for tr in tr1 if tr}
    trs = [re.match(r'((\w|\|)+--)*(?P<fr>(\w|\|)+)->(?P<to>(\w|\|)+)', st) for st in dcs]
    trs = {tr.group('fr'): {'Dist': tr.group('fr'), 'To': tr.group('to')} for tr in trs if tr}
    trs.update(tr1)
    links = [re.match(r'(?P<fr>(\w|\|)+)--(?P<to>(\w|\|)+)', st) for st in dcs]

    for link in links:
        if link:
            targets[link.group('fr')].append(link.group('to'))

    js['Transitions'] = trs
    js['Targets'] = targets
    return js


def restore_CTBN_from_json(js):
    bp = BlueprintCTBN(js['ModelName'])
    if 'Order' in js:
        for ms in js['Order']:
            bp.add_microstate(ms, js['Microstates'][ms])
    for ms, vs in js['Microstates'].items():
        bp.add_microstate(ms, vs)
    for st, std in js['States'].items():
        bp.add_state(st, **std)
    for tr, trd in js['Transitions'].items():
        bp.add_transition(tr, trd['To'], trd['Dist'])
    for fr, trs in js['Targets'].items():
        for tr in trs:
            bp.link_state_transition(fr, tr)
    return bp


def restore_CTMC_from_json(js):
    bp = BlueprintCTMC(js['ModelName'])
    for st in js['States']:
        bp.add_state(st)
    for tr, trd in js['Transitions'].items():
        bp.add_transition(tr, trd['To'], trd['Dist'])
    for fr, trs in js['Targets'].items():
        for tr in trs:
            bp.link_state_transition(fr, tr)
    return bp


def restore_dcore_from_json(js):
    try:
        m = js['ModelType']
    except KeyError:
        raise KeyError('Model type is not identifiable')

    if m == 'CTBN':
        return restore_CTBN_from_json(js)
    elif m == 'CTMC':
        return restore_CTMC_from_json(js)

    raise KeyError('Model type does not exist')


def restore_dcore_from_script(scr):
    js = script_to_json(scr)
    return restore_dcore_from_json(js)
