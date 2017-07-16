from dzdy.command import *
from json import JSONDecodeError
import logging

log = logging.getLogger(__name__)

__author__ = 'TimeWz667'


class Director:
    def __init__(self):
        self.PCores = dict()
        self.DCores = dict()
        self.MCores = dict()
        self.Layouts = dict()

    def __add_pc(self, pc):
        if pc in self.PCores:
            log.info('Override parameter core {}'.format(pc))
        else:
            log.info('Added parameter core {}'.format(pc))
        self.PCores[pc.Name] = pc

    def __add_dc(self, dc):
        self.DCores[dc.Name] = dc

    def __add_mc(self, mc):
        self.MCores[mc.Name] = mc

    def __add_layout(self, layout):
        self.Layouts[layout.Name] = layout

    def get_pc(self, pc):
        return self.PCores[pc]

    def get_dc(self, dc):
        return self.DCores[dc]

    def get_mc(self, mc):
        return self.MCores[mc]

    def get_layout(self, layout):
        return self.Layouts[layout]

    def read_pc(self, script):
        pc = read_pcore(script)
        self.__add_pc(pc)

    def read_dc(self, script):
        dc = read_dcore(script)
        self.__add_dc(dc)

    def load_pc(self, file, js=True):
        if js:
            try:
                pc = load_pcore(load_json(file))
            except JSONDecodeError:
                pc = read_pcore(load_txt(file))
        else:
            pc = read_pcore(load_txt(file))
        self.__add_pc(pc)

    def load_dc(self, file, js=True):
        if js:
            try:
                dc = load_dcore(load_json(file))
            except JSONDecodeError:
                dc = read_dcore(load_txt(file))
        else:
            dc = read_dcore(load_txt(file))
        self.__add_dc(dc)

    def load_mc(self, file):
        mc = load_mcore(load_json(file))
        self.__add_mc(mc)

    def load_layout(self, file):
        lo = load_layout(load_json(file))
        self.__add_layout(lo)

    def new_dc(self, name, dc_type='CTBN'):
        dc = new_dcore(name, dc_type)
        self.__add_dc(dc)
        return dc

    def new_mc(self, name, mc_type='ABM', **kwargs):
        mc = new_mcore(name, mc_type, **kwargs)
        self.__add_mc(mc)
        return mc

    def new_layout(self, name):
        lo = new_layout(name)
        self.__add_layout(lo)
        return lo

    def list_pc(self):
        return list(self.PCores.keys())

    def list_dc(self):
        return list(self.DCores.keys())

    def list_mc(self):
        return list(self.MCores.keys())

    def list_layout(self):
        return list(self.Layouts.keys())

    def save_pc(self, pc, file):
        try:
            pc = self.get_pc(pc)
        except KeyError:
            # todo logging
            pass
        save_pcore(pc, file)

    def save_dc(self, dc, file):
        try:
            dc = self.get_dc(dc)
        except KeyError:
            # todo logging
            pass
        save_dcore(dc, file)

    def save_mc(self, mc, file):
        try:
            mc = self.get_mc(mc)
        except KeyError:
            # todo logging
            pass
        save_mcore(mc, file)

    save_pcore = save_pc
    load_pcore = load_pc
    read_pcore = read_pc
    list_pcore = list_pc
    save_dcore = save_dc
    load_dcore = load_dc
    read_dcore = read_dc
    list_dcore = list_dc
    save_mcore = save_mc
    load_mcore = load_mc
    list_mcore = list_mc

    def save_layout(self, ly, file):
        try:
            ly = self.get_layout(ly)
        except KeyError:
            # todo logging
            pass
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
        self.PCores.update({k: load_pcore(v) for k, v in js['PCores'].items()})
        self.DCores.update({k: load_dcore(v) for k, v in js['DCores'].items()})
        self.MCores.update({k: load_mcore(v) for k, v in js['MCores'].items()})
        self.Layouts.update({k: load_layout(v) for k, v in js['Layouts'].items()})

    def generate_pc_dc(self, pc, dc, new_name=None):
        return generate_pc_dc(self.PCores[pc], self.DCores[dc], new_name=new_name)

    def generate_mc(self, mc, name=None):
        if isinstance(self.MCores[mc], BlueprintABM):
            return self.generate_abm(mc, name)
        else:
            # todo
            return None

    def generate_abm(self, mc, name=None):
        if not name:
            name = mc
        mc = self.MCores[mc]
        pc, dc = mc.TargetedPCore, mc.TargetedDCore
        pc, dc = self.generate_pc_dc(pc, dc, name)
        return generate_abm(mc, pc, dc, name)

    def new_abm(self, name, tar_pcore, tar_dcore):
        bp_abm = new_abm(name, tar_pcore, tar_dcore)
        self.MCores[name] = bp_abm
        return bp_abm

    def copy_abm(self, mod_src, tr_tte=True, pc_new=None):
        # copy model structure
        pc, dc, mc = mod_src.Meta

        return copy_abm(mod_src, self.MCores[mc], self.PCores[pc], self.DCores[dc], tr_tte=tr_tte, pc_new=pc_new)

    def generate(self, model):
        try:
            lyo = self.Layouts[model]
            return lyo.generate(self.generate_mc)
        except KeyError:
            # todo logging
            pass

    def simulate(self, model, to, y0=None, fr=0, dt=1):
        if model in self.Layouts:
            m, y0 = self.generate(model)
        elif model in self.MCores and y0:
            m = self.generate_abm(model)
        else:
            # todo logging
            pass
        out = simulate(m, y0=y0, fr=fr, to=to, dt=dt)
        return m, out

    def update(self, model, to, dt=1):
        out = update(model, to, dt)
        return model, out


class DirectorABM(Director):
    def __init__(self):
        Director.__init__(self)

