import epidag as dag
from .misc import *
from .dcore.fn import *
from .mcore import Simulator
import complexism.agentbased.statespace as ssa
import complexism.equationbased as ebm

__author__ = 'TimeWz667'
__all__ = [
    'load_txt', 'load_json', 'save_json',
    'read_bn_script', 'read_bn_json', 'save_bn',
    'new_dbp', 'read_dbp_json', 'read_dbp_script', 'save_dbp',
    'new_mbp',
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
