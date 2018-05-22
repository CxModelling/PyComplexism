from json import JSONDecodeError
import logging
import epidag as dag
from complexism.fn import *

log = logging.getLogger(__name__)

__author__ = 'TimeWz667'
__all__ = ['Director']


class Director:
    def __init__(self):
        self.BayesianNetworks = dict()
        self.DCoreBlueprints = dict()
        self.MCoreBlueprints = dict()
        self.ModelLayouts = dict()

    def _add_bn(self, bn):
        if bn in self.BayesianNetworks:
            log.info('Bayesian Network {} have already existed'.format(bn.Name))
        else:
            self.BayesianNetworks[bn.Name] = bn
            log.info('Bayesian Network {} added'.format(bn.Name))

    def _add_dbp(self, dbp):
        if dbp in self.DCoreBlueprints:
            log.info('DCore Blueprint {} overrided'.format(dbp.Name))
        else:
            self.DCoreBlueprints[dbp.Name] = dbp
            log.info('DCore Blueprint {} added'.format(dbp.Name))

    def _add_mbp(self, mbp):
        if mbp in self.MCoreBlueprints:
            log.info('MCore Blueprint {} overrided'.format(mbp.Name))
        else:
            self.MCoreBlueprints[mbp.Name] = mbp
            log.info('MCore Blueprint {} added'.format(mbp.Name))

    def _add_lyo(self, lyo):
        if lyo in self.ModelLayouts:
            log.info('Model layout {} overrided'.format(lyo.Name))
        else:
            self.ModelLayouts[lyo.Name] = lyo
            log.info('Model layout {} added'.format(lyo.Name))

    def get_bn(self, bn_name):
        return self.BayesianNetworks[bn_name]

    def get_dbp(self, dbp_name):
        return self.DCoreBlueprints[dbp_name]

    def get_mbp(self, mbp_name):
        return self.MCoreBlueprints[mbp_name]

    def get_lyo(self, lyo_name):
        return self.ModelLayouts[lyo_name]

    def read_bn_script(self, script):
        bn = read_bn_script(script)
        self._add_bn(bn)

    def load_bn(self, file):
        try:
            bn = read_bn_json(load_json(file))
        except JSONDecodeError:
            bn = read_bn_script(load_txt(file))
        self._add_bn(bn)

    def save_bn(self, bn_name, file):
        try:
            bn = self.get_bn(bn_name)
            save_bn(bn, file)
        except KeyError:
            log.warning('Bayesian Network {} not found'.format(bn_name))

    def list_bns(self):
        return list(self.BayesianNetworks.keys())

    def read_dbp_script(self, script):
        bn = read_dbp_script(script)
        self._add_bn(bn)

    def load_dbp(self, file):
        try:
            dbp = read_dbp_json(load_json(file))
        except JSONDecodeError:
            dbp = read_dbp_script(load_txt(file))
        self._add_dbp(dbp)

    def new_dbp(self, dbp_name, dc_type):
        """
        Generate a new blueprint of a dynamic core
        :param dbp_name: name of the model
        :param dc_type: type of dynamic core, CTBN or CTMC
        :return: a new Blueprint
        """
        dbp = new_dbp(dbp_name, dc_type)
        self._add_dbp(dbp)
        return dbp

    def save_dbp(self, dbp_name, file):
        try:
            dbp = self.get_dbp(dbp_name)
            save_dbp(dbp, file)
        except KeyError:
            log.warning('DCore Blueprint {} not found'.format(dbp_name))

    def list_dbps(self):
        return list(self.DCoreBlueprints.keys())

    def load_mbp(self, file):
        try:
            mbp = read_mbp_json(load_json(file))
        except JSONDecodeError:
            mbp = read_mbp_script(load_txt(file))
        self._add_mbp(mbp)

    def new_mbp(self, mbp_name, model_type):
        """
        Generate a new blueprint of a dynamic core
        :param mbp_name: name of the model
        :param model_type: type of simulation model, SSABM, SSODE, ODE
        :return: a new Blueprint
        """
        mbp = new_mbp(mbp_name, model_type)
        self._add_mbp(mbp)
        return mbp

    def save_mbp(self, mbp_name, file):
        try:
            mbp = self.get_mbp(mbp_name)
            save_mbp(mbp, file)
        except KeyError:
            log.warning('Model Blueprint {} not found'.format(mbp_name))

    def list_mbps(self):
        return list(self.MCoreBlueprints.keys())

    def save_layout(self, lyo_name, file):
        try:
            lyo = self.get_lyo(lyo_name)
            save_layout(lyo, file)
        except KeyError:
            log.info('Layout {} saved'.format(lyo))

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
        js = load_json(file)
        self.BayesianNetworks.update({k: read_bn_json(v) for k, v in js['PCores'].items()})
        self.DCoreBlueprints.update({k: read_dbp_json(v) for k, v in js['DCores'].items()})
        # self.MCoreBlueprints.update({k: load_mc(v) for k, v in js['MCores'].items()})
        # self.ModelLayouts.update({k: load_layout(v) for k, v in js['Layouts'].items()})

    def generate_model(self, mc, name=None, **kwargs):
        if not name:
            name = mc
        mbp = self.get_mbp(mc)
        if 'bn' in kwargs:
            kwargs['bn'] = self.get_bn(kwargs['bn'])
        if 'dbp' in kwargs:
            kwargs['dbp'] = self.get_dbp(kwargs['dbp'])
        if 'dc' in kwargs:
            kwargs['dc'] = self.get_dbp(kwargs['dc'])

        return mbp.generate('M1', **kwargs)

    def copy_model(self, mod_src, **kwargs):
        pass

    def generate(self, model, cond=None, fixed=None, odt=0.5):
        if fixed is None:
            fixed = list()

        try:
            lyo = self.ModelLayouts[model]
            return lyo.generate(self.generate_model, odt, fixed=fixed, cond=cond)
        except KeyError:
            # todo logging
            pass

    def simulate(self, model, to, y0=None, fr=0, dt=1, fixed=None, cond=None):
        if model in self.ModelLayouts:
            m, y0 = self.generate(model, odt=dt/2, cond=cond, fixed=fixed)
        elif model in self.MCoreBlueprints and y0:
            m = self.generate_model(model)
        else:
            log.warning('No matched model')
            return

        out = simulate(m, y0=y0, fr=fr, to=to, dt=dt)
        return m, out

    def update(self, model, to, dt=1):
        out = update(model, to, dt)
        return out
