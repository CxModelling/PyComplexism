import re
from dcore import *

__author__ = 'TimeWz667'


def build_from_json(js):
    m = re.search(r'\"ModelType\":\s*\"(\S+)\"', js)
    m = m.group(1)
    if m == 'CTBN':
        return BluePrintCTBN.from_json(js)
    elif m == 'CTMC':
        return BluePrintCTMC.from_json(js)
    raise KeyError('No such model type')
