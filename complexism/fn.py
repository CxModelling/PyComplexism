import epidag as dag
from .misc import *
from .dcore.fn import *
from .mcore import Simulator
import complexism.agentbased.statespace as ssa
import complexism.equationbased as ebm
import complexism.multimodel as mm

__author__ = 'TimeWz667'
__all__ = [
    'load_txt', 'load_json', 'save_json',
    'read_bn_script', 'read_bn_json', 'save_bn',
    'new_dbp', 'read_dbp_json', 'read_dbp_script', 'save_dbp',
    'new_mbp', # 'read_mbp_json', 'save_mbp',
    'new_lyo', 'read_lyo_json', 'save_lyo',
    'simulate', 'update'
]


def read_bn_script(script):
    """
    Read a Bayesian Network from a script
    :param script: script of pc
    :return: a blueprint of parameter core
    """
    return dag.bn_from_script(script)


def read_bn_json(js):
    """
    Load a Bayesian Network from json format
    :param js: json object
    :return: a blueprint of parameter core
    """
    return dag.bn_from_json(js)


def save_bn(bn, path):
    """
    Save a Bayesian Network
    :param bn: Bayesian Network
    :type bn: BayesianNetwork
    :param path: path of file
    """
    save_json(bn.to_json(), path)


def new_mbp(name, model_type='SSABM'):
    """
    Generate a new blueprint of model
    :param name: name of blueprint
    :param model_type: type of model
    :return: blueprint of model
    """
    if model_type == 'SSABM':
        return ssa.BlueprintStSpABM(name)
    elif model_type == 'ODEABM':
        pass
    elif model_type == 'ODE':
        return ebm.BlueprintODE(name)
    elif model_type == 'SSODE':
        pass
    else:
        pass


def read_mbp_json(js):
    """
    Read a model blueprint from a json file
    :param js: json formatted model blueprint
    :return: model blueprint
    """
    if js['Type'] == 'SSABM':
        return ssa.BlueprintStSpABM.from_json(js)
    elif js['Type'] == 'ODEABM':
        pass
    elif js['Type'] == 'ODE':
        return ebm.BlueprintODE.from_json(js)
    elif js['Type'] == 'SSODE':
        pass
    else:
        pass


def save_mbp(mbp, path):
    """
    Output model layout to file system
    :param mbp: model blueprint
    :param path: file path
    """
    save_json(mbp.to_json(), path)


def read_lyo_json(js):
    """
    Load model layout from json format
    :param js: json
    :return: model layout
    """
    return mm.ModelLayout.from_json(js)


def new_lyo(name):
    """
    Generate a new blueprint of layout
    :param name: name of blueprint
    :return: blueprint of layout
    """
    return mm.ModelLayout(name)


def save_lyo(layout, path):
    """
    Output model layout to file system
    :param layout: model layout
    :param path: file path
    """
    save_json(layout.to_json(), path)


def simulate(model, y0, fr, to, dt=1):
    """
    Simulate a dynamic model with initial values (y0)
    :param model: dynamic model
    :param y0: initial value
    :param fr: initial time point
    :param to: end time
    :param dt: observation interval
    :return: data of simulation
    """
    if model.TimeEnd:
        return model.output()
    sim = Simulator(model)
    sim.simulate(y0, fr, to, dt)
    return model.output()


def update(model, to, dt=1):
    """
    Update a dynamic to a certain time point
    :param model: dynamic model which has been initialised
    :param to: end time
    :param dt: observation interval
    :return: data of simulation
    """
    sim = Simulator(model)
    sim.Time = model.TimeEnd
    if to > sim.Time:
        sim.update(to, dt)
    return model.output()
