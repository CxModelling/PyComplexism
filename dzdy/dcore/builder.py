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
