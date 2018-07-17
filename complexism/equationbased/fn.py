import epidag as dag
from complexism.equationbased import OrdinaryDifferentialEquationModel

__author__ = 'TimeWz667'
__all__ = ['prepare_pc', 'generate_ode_model', 'set_observations']


def prepare_pc(model_name, **kwargs):
    if 'pc' in kwargs:
        pc = kwargs['pc']
    elif 'sm' in kwargs:
        sm = kwargs['sm']
        pc = sm.generate(model_name, exo=kwargs['exo'] if 'exo' in kwargs else None)
    elif 'bn' in kwargs:
        bn = kwargs['bn']
        random = kwargs['random'] if 'random' in kwargs else []
        hie = kwargs['hie'] if 'hie' in kwargs else {model_name: []}
        sm = dag.as_simulation_core(bn, hie=hie, random=random, out=list())
        pc = sm.generate(model_name, exo=kwargs['exo'] if 'exo' in kwargs else None)
    else:
        raise KeyError('Parameter core not identified')
    return pc


def generate_ode_model(model_name, ode, pc, y_names, x=None, fdt=0.1, dt=0.5):
    fdt = min([fdt, dt])
    model = OrdinaryDifferentialEquationModel(model_name, ode, ys=y_names, dt=fdt, odt=dt, xs=x, env=pc)
    return model


def set_observations(model, stocks=list(), stock_functions=list(), flow_functions=list()):
    # Assign observations
    for st in stocks:
        model.add_observing_stock(st)
    for func in stock_functions:
        model.add_observing_stock_function(func)
    for func in flow_functions:
        model.add_observing_flow_function(func)
