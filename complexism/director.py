from json import JSONDecodeError
import logging
import epidag as dag
from complexism.fn import *

__author__ = 'TimeWz667'
__all__ = ['Director']


class Director:
    def __init__(self):
        self.BayesianNetworks = dict()
        self.DCoreBlueprints = dict()
        self.MCoreBlueprints = dict()
        self.ModelLayouts = dict()
        self.Log = logging.getLogger(__name__)

    def _add_bn(self, bn):
        if bn in self.BayesianNetworks:
            self.Log.warning('Bayesian Network {} have already existed'.format(bn.Name))
        else:
            self.BayesianNetworks[bn.Name] = bn
            self.Log.info('Bayesian Network {} added'.format(bn.Name))

    def _add_dbp(self, dbp):
        if dbp in self.DCoreBlueprints:
            self.Log.warning('State-Space Model {} have already existed'.format(dbp.Name))
        else:
            self.DCoreBlueprints[dbp.Name] = dbp
            self.Log.info('State-Space Model {} added'.format(dbp.Name))

    def _add_mbp(self, mbp):
        if mbp in self.MCoreBlueprints:
            self.Log.warning('Simulation Model {} have already existed'.format(mbp.Name))
        else:
            self.MCoreBlueprints[mbp.Name] = mbp
            self.Log.info('Simulation Model {} added'.format(mbp.Name))

    def _add_lyo(self, lyo):
        if lyo in self.ModelLayouts:
            self.Log.warning('Model Layout {} have already existed'.format(lyo.Name))
        else:
            self.ModelLayouts[lyo.Name] = lyo
            self.Log.info('Model Layout {} added'.format(lyo.Name))

    def get_bayes_net(self, bn_name):
        try:
            return self.BayesianNetworks[bn_name]
        except KeyError:
            self.Log.warning('Unknown BayesNet')

    def get_state_space_model(self, dbp_name):
        try:
            return self.DCoreBlueprints[dbp_name]
        except KeyError:
            self.Log.warning('Unknown State-Space Model')

    def get_sim_model(self, mbp_name):
        try:
            return self.MCoreBlueprints[mbp_name]
        except KeyError:
            self.Log.warning('Unknown Simulation Model')

    def get_model_layout(self, lyo_name):
        try:
            return self.ModelLayouts[lyo_name]
        except KeyError:
            self.Log.warning('Unknown Model Layout')

    def read_bayes_net(self, script):
        bn = read_bn_script(script)
        self._add_bn(bn)

    def load_bayes_net(self, file):
        try:
            bn = read_bn_json(load_json(file))
        except JSONDecodeError:
            bn = read_bn_script(load_txt(file))
        self._add_bn(bn)

    def save_bayes_net(self, bn_name, file):
        try:
            bn = self.get_bayes_net(bn_name)
            save_bn(bn, file)
        except KeyError:
            self.Log.warning('BayesNet {} not found'.format(bn_name))

    def list_bayes_nets(self):
        return list(self.BayesianNetworks.keys())

    def read_state_space_model(self, script):
        bn = read_dbp_script(script)
        self._add_dbp(bn)

    def load_state_space_model(self, file):
        try:
            dbp = read_dbp_json(load_json(file))
        except JSONDecodeError:
            dbp = read_dbp_script(load_txt(file))
        self._add_dbp(dbp)

    def new_state_space_model(self, dbp_name, dc_type):
        """
        Generate a new blueprint of a state-space dynamic model
        :param dbp_name: name of the model
        :param dc_type: type of dynamic core, CTBN or CTMC
        :return: a new Blueprint
        """
        dbp = new_dbp(dbp_name, dc_type)
        self._add_dbp(dbp)
        return dbp

    def save_state_space_model(self, dbp_name, file):
        try:
            dbp = self.get_state_space_model(dbp_name)
            save_dbp(dbp, file)
        except KeyError:
            self.Log.warning('Unknown State-Space Model')

    def list_state_spaces(self):
        return list(self.DCoreBlueprints.keys())

    def load_sim_model(self, file):
        # todo
        try:
            mbp = read_mbp_json(load_json(file))
        except JSONDecodeError:
            raise TypeError('Unknown format')
            #mbp = read_mbp_script(load_txt(file))
        self._add_mbp(mbp)

    def new_sim_model(self, mbp_name, model_type):
        """
        Generate a new blueprint of a dynamic core
        :param mbp_name: name of the model
        :param model_type: type of simulation model, StSpABM, SSODE, ODEEBM
        :return: a new Blueprint
        """
        mbp = new_mbp(mbp_name, model_type)
        self._add_mbp(mbp)
        return mbp

    def save_sim_model(self, mbp_name, file):
        # todo
        try:
            mbp = self.get_sim_model(mbp_name)
            save_mbp(mbp, file)
        except KeyError:
            self.Log.warning('Model Blueprint {} not found'.format(mbp_name))

    def list_sim_models(self):
        return list(self.MCoreBlueprints.keys())

    def new_model_layout(self, name):
        layout = new_lyo(name)
        self._add_lyo(layout)
        return layout

    def save_layout(self, lyo_name, file):
        # todo
        lyo = self.get_model_layout(lyo_name)
        save_lyo(lyo, file)
        self.Log.info('Layout {} saved'.format(lyo))

    def list_lyo(self):
        return list(self.ModelLayouts.keys())

    def save(self, file):
        js = dict()
        js['PCores'] = {k: v.to_json() for k, v in self.BayesianNetworks.items()}
        js['DCores'] = {k: v.to_json() for k, v in self.DCoreBlueprints.items()}
        js['MCores'] = {k: v.to_json() for k, v in self.MCoreBlueprints.items()}
        js['Layouts'] = {k: v.to_json() for k, v in self.ModelLayouts.items()}
        save_json(js, file)

    def load(self, file):
        # todo
        js = load_json(file)
        self.BayesianNetworks.update({k: read_bn_json(v) for k, v in js['PCores'].items()})
        self.DCoreBlueprints.update({k: read_dbp_json(v) for k, v in js['DCores'].items()})
        # self.MCoreBlueprints.update({k: load_mc(v) for k, v in js['MCores'].items()})
        # self.ModelLayouts.update({k: load_layout(v) for k, v in js['Layouts'].items()})

    def generate_mc(self, name, sim_model, **kwargs):
        mbp = self.get_sim_model(sim_model)
        kwargs['da'] = self
        return mbp.generate(name, **kwargs)

    def _generate_lyo(self, name, layout, bn, all_obs=True, exo=None):
        lyo = self.get_model_layout(layout)
        if isinstance(bn, str):
            bn = self.get_bayes_net(bn)
        sm = dag.as_simulation_core(bn, lyo.get_parameter_hierarchy(self))
        pc = sm.generate(name, exo=exo)
        return lyo.generate(name, self, pc, all_obs=all_obs)

    def generate_model(self, name, sim_model, bn):
        if isinstance(bn, str):
            bn = self.get_bayes_net(bn)

        if sim_model in self.ModelLayouts:
            return self._generate_lyo(name, sim_model, bn=bn)
        else:
            return self.generate_mc(name, sim_model, bn=bn)

    def get_y0s(self, layout):
        lyo = self.get_model_layout(layout)
        return lyo.get_y0s()

    def copy_model(self, mod_src, **kwargs):
        # todo
        pass
