import re
from misc import save_json
from .ctbn import BlueprintCTBN
from .ctmc import BlueprintCTMC


__author__ = 'TimeWz667'
__all__ = ['new_dbp', 'read_dbp_json', 'read_dbp_script', 'save_dbp']


def script_to_json(scr):
    dcs = scr.split('\n')
    while dcs:
        dc = dcs[0]
        pars = re.match(r'(?P<Type>CTBN|CTMC)\s+(?P<Name>\w+)\s*', dc, re.I)
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


def new_dbp(name, dc_type='CTMC'):
    """
    Generate a new blueprint of a dynamic core
    :param name: name of the model
    :param dc_type: type of dynamic core, CTBN or CTMC
    :return: a new Blueprint
    """
    if dc_type == 'CTMC':
        return BlueprintCTMC(name)
    elif dc_type =='CTBN':
        return BlueprintCTBN(name)
    else:
        raise TypeError('Unknown DCore type')


def read_dbp_json(js):
    """
    Read a DC from a json object
    :param js: script of dc
    :return: a blueprint of dynamic core
    """
    try:
        m = js['ModelType']
    except KeyError:
        raise KeyError('Model type is not identifiable')

    if m == 'CTBN':
        return BlueprintCTBN.from_json(js)
    elif m == 'CTMC':
        return BlueprintCTMC.from_json(js)
    raise KeyError('Model type does not exist')


def read_dbp_script(script):
    """
    Read a DC from a script
    :param script: script of dc
    :return: a blueprint of dynamic core
    """
    js = script_to_json(script)
    return read_dbp_json(js)


def save_dbp(dbp, path):
    """
    Output a blueprint of dynamic core to file system
    :param dc: dynamic core
    :param path: file path
    """
    save_json(dbp.to_json(), path)
