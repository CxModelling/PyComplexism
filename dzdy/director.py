from dzdy.command import *
from json import JSONDecodeError
import logging

log = logging.getLogger(__name__)

__author__ = 'TimeWz667'


class DirectorDCPC:
    def __init__(self):
        self.PCores = dict()
        self.DCores = dict()

    def __add_pc(self, pc):
        if pc in self.PCores:
            log.info('Parameter core {} overrided'.format(pc))
        else:
            log.info('Parameter core {} added'.format(pc))
        self.PCores[pc.Name] = pc

    def __add_dc(self, dc):
        if dc in self.DCores:
            log.info('Dynamic core {} overrided'.format(dc))
        else:
            log.info('Dynamic core {} added'.format(dc))
        self.DCores[dc.Name] = dc

    def get_pc(self, pc):
        return self.PCores[pc]

    def get_dc(self, dc):
        return self.DCores[dc]

    def read_pc(self, script):
        pc = read_pc(script)
        self.__add_pc(pc)

    def read_dc(self, script):
        dc = read_dc(script)
        self.__add_dc(dc)

    def load_pc(self, file, ):
        try:
            pc = load_pc(load_json(file))
        except JSONDecodeError:
            pc = read_pc(load_txt(file))

        self.__add_pc(pc)

    def load_dc(self, file):
        try:
            dc = load_dc(load_json(file))
        except JSONDecodeError:
            dc = read_dc(load_txt(file))

        self.__add_dc(dc)

    def new_dc(self, name, dc_type='CTBN'):
        dc = new_dc(name, dc_type)
        self.__add_dc(dc)
        return dc

    def list_pc(self):
        return list(self.PCores.keys())

    def list_dc(self):
        return list(self.DCores.keys())

    def save_pc(self, pc, file):
        try:
            pc = self.get_pc(pc)
        except KeyError:
            # todo logging
            pass
        save_pc(pc, file)

    def save_dc(self, dc, file):
        try:
            dc = self.get_dc(dc)
        except KeyError:
            # todo logging
            pass
        save_dc(dc, file)

    def save(self, file):
        js = dict()
        js['PCores'] = {k: v.to_json() for k, v in self.PCores.items()}
        js['DCores'] = {k: v.to_json() for k, v in self.DCores.items()}
        save_json(js, file)

    def load(self, file):
        js = load_json(file)
        self.PCores.update({k: load_pc(v) for k, v in js['PCores'].items()})
        self.DCores.update({k: load_dc(v) for k, v in js['DCores'].items()})

    # functions in old version
    save_pcore = save_pc
    load_pcore = load_pc
    read_pcore = read_pc
    list_pcore = list_pc
    save_dcore = save_dc
    load_dcore = load_dc
    read_dcore = read_dc
    list_dcore = list_dc


class Director(DirectorDCPC):
    def __init__(self):
        DirectorDCPC.__init__(self)
        self.MCores = dict()
        self.Layouts = dict()

    def __add_mc(self, mc):
        self.MCores[mc.Name] = mc

    def __add_layout(self, layout):
        self.Layouts[layout.Name] = layout

    def get_mc(self, mc):
        return self.MCores[mc]

    def get_layout(self, layout):
        return self.Layouts[layout]

    def load_mc(self, file):
        mc = load_mc(load_json(file))
        self.__add_mc(mc)

    def load_layout(self, file):
        lo = load_layout(load_json(file))
        self.__add_layout(lo)

    def new_mc(self, name, mc_type='ABM', **kwargs):
        mc = new_mc(name, mc_type, **kwargs)
        self.__add_mc(mc)
        return mc

    def new_layout(self, name):
        lo = new_layout(name)
        self.__add_layout(lo)
        return lo

    def list_mc(self):
        return list(self.MCores.keys())

    def list_layout(self):
        return list(self.Layouts.keys())

    def save_mc(self, mc, file):
        try:
            mc = self.get_mc(mc)
        except KeyError:
            # todo logging
            pass
        save_mc(mc, file)

    save_mcore = save_mc
    load_mcore = load_mc
    list_mcore = list_mc

    def save_layout(self, ly, file):
        try:
            ly = self.get_layout(ly)
        except KeyError:
            log.info('Layout {} saved'.format(ly))
        save_layout(ly, file)

    def save(self, file):
        js = dict()
        js['PCores'] = {k: v.to_json() for k, v in self.PCores.items()}
        js['DCores'] = {k: v.to_json() for k, v in self.DCores.items()}
        js['MCores'] = {k: v.to_json() for k, v in self.MCores.items()}
        js['Layouts'] = {k: v.to_json() for k, v in self.Layouts.items()}
        save_json(js, file)

    def load(self, file):
        js = load_json(file)
        self.PCores.update({k: load_pc(v) for k, v in js['PCores'].items()})
        self.DCores.update({k: load_dc(v) for k, v in js['DCores'].items()})
        self.MCores.update({k: load_mc(v) for k, v in js['MCores'].items()})
        self.Layouts.update({k: load_layout(v) for k, v in js['Layouts'].items()})

    def generate_model(self, mc, name=None, pc=None, dc=None, **kwargs):
        if not name:
            name = mc
        mc = self.MCores[mc]
        if mc.require_pc:
            pc = pc if pc else generate_pc(self.PCores[mc.TargetedPCore])
            if mc.require_dc:
                dc = dc if dc else generate_dc(self.DCores[mc.TargetedDCore], pc)

        return generate_model(mc, pc, dc, name, **kwargs)

    def copy_model(self, mod_src, tr_tte=True, pc_new=None, intervention=None):
        # copy model structure
        pc, dc, mc = mod_src.Meta
        if pc: pc = self.PCores[pc]
        if dc: dc = self.DCores[dc]
        if mc: mc = self.MCores[mc]

        return copy_model(mod_src, mc, pc, dc, tr_tte=tr_tte, pc_new=pc_new, intervention=intervention)

    def generate(self, model, random_effect=False):
        try:
            lyo = self.Layouts[model]
            return lyo.generate(self.generate_model)
        except KeyError:
            # todo logging
            pass

    def simulate(self, model, to, y0=None, fr=0, dt=1):
        if model in self.Layouts:
            m, y0 = self.generate(model)
        elif model in self.MCores and y0:
            m = self.generate_model(model)
        else:
            # todo logging
            raise ValueError('No match model')

        out = simulate(m, y0=y0, fr=fr, to=to, dt=dt)
        return m, out

    def update(self, model, to, dt=1):
        out = update(model, to, dt)
        return out


#class DirectorABM(Director):
#    def __init__(self):
#        Director.__init__(self)

