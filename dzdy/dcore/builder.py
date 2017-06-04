import re
from dzdy.dcore import *

__author__ = 'TimeWz667'


def build_from_json(js):
    if isinstance(js, str):
        m = re.search(r'\"ModelType\":\s*\"(\S+)\"', js)
        m = m.group(1)
    else:
        m = js['ModelType']

    if m == 'CTBN':
        return BluePrintCTBN.from_json(js)
    elif m == 'CTMC':
        return BluePrintCTMC.from_json(js)
    raise KeyError('No such model type')


def build_from_script(scr):
    dcs = scr.split('\n')
    dcs = [re.sub(r'\s+', '', st) for st in dcs]
    dcs = [re.sub(r'#\w+', '', st) for st in dcs if st is not '']

    pars = [re.match(r'(?P<par>\w+)=(?P<val>\w+)', st) for st in dcs]
    pars = {par['par']: par['val'] for par in pars if par}
    js = {'ModelName': pars['Name'], 'ModelType': pars['Type']}

    if pars['Type'] == 'CTBN':
        mss = [re.match(r'(?P<node>\w+)\[(?P<ms>(\w|\|)+)\]', st) for st in dcs]
        mss = {ms['node']: ms['ms'].split('|') for ms in mss if ms}

        sts = [re.match(r'(?P<state>(\w|\|)+)\{(?P<ms>(.*)+)\}', st) for st in dcs]
        sts = {st['state']: dict(re.findall(r'(?P<a>\w+):(?P<b>\w+)', st['ms'])) for st in sts if st}
        targets = {st: list() for st in sts.keys()}
        js['Microstates'] = mss
        js['States'] = sts

    elif pars['Type'] == 'CTMC':
        sts = [re.match(r'(?P<state>\A(\w|\|)+\Z)', st) for st in dcs]
        sts = [st['state'] for st in sts if st]
        targets = {st: list() for st in sts}

        js['States'] = sts

    else:
        raise SyntaxError('Can not specify model type')

    tr1 = [re.match(r'((\w|\|)+--)*(?P<fr>(\w|\|)+)\((?P<by>\w+)\)->(?P<to>(\w|\|)+)', st) for st in dcs]
    tr1 = {tr['fr']: {'Dist': tr['by'], 'To': tr['to']} for tr in tr1 if tr}
    trs = [re.match(r'((\w|\|)+--)*(?P<fr>(\w|\|)+)->(?P<to>(\w|\|)+)', st) for st in dcs]
    trs = {tr['fr']: {'Dist': tr['fr'], 'To': tr['to']} for tr in trs if tr}
    trs.update(tr1)
    links = [re.match(r'(?P<fr>(\w|\|)+)--(?P<to>(\w|\|)+)', st) for st in dcs]

    for link in links:
        if link:
            targets[link['fr']].append(link['to'])

    js['Transitions'] = trs
    js['Targets'] = targets
    return build_from_json(js)
