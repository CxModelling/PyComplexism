from dzdy import *
import pcore

__author__ = 'TimeWz667'


class DirectorABM:
    def __init__(self):
        self.PCores = dict()
        self.DCores = dict()
        self.MCores = dict()

    def add_pcore(self, name, pc):
        if isinstance(pc, pcore.SimulationModel):
            self.PCores[name] = pc
            print('PCore {} added'.format(name))
        else:
            print('Adding failed')

    def read_pcore(self, name, script):
        pc = pcore.DirectedAcyclicGraph(script).get_simulation_model()
        self.add_pcore(name, pc)

    def restore_pcore(self, name, js):
        pc = pcore.SimulationModel.build_from_json(js)
        self.add_pcore(name, pc)

    def add_dcore(self, dc):
        if isinstance(dc, AbsBluePrint):
            self.DCores[dc.Name] = dc
            print('Dcore {} added'.format(dc.Name))
        else:
            print('Adding failed')

    def read_dcore(self, script):
        bp = build_from_script(script)
        self.add_dcore(bp)

    def restore_dcore(self, js):
        bp = build_from_json(js)
        self.add_dcore(bp)

    def get_pcore(self, name):
        return self.PCores[name]

    def get_dcore(self, name):
        return self.DCores[name]

    def list_pcores(self):
        print(list(self.PCores.keys()))

    def list_dcores(self):
        print(list(self.DCores.keys()))

    def generate_pc_dc(self, pc, dc, new_name=None):
        pc = self.PCores[pc].sample_core()
        dc = self.DCores[dc]
        if not dc.is_compatible(pc):
            raise ValueError('Not compatible pcore')
        return pc, dc.generate_model(pc, new_name)

    def generate_abm(self, mc, name=None):
        if not name:
            name = mc
        mc = self.MCores[mc]
        pc, dc = mc.TargetedPCore, mc.TargetedDCore
        pc, dc = self.generate_pc_dc(pc, dc, name)
        return mc.generate(name, pc, dc)

    def new_abm(self, name, tar_pcore, tar_dcore):
        bp_abm = AgentBasedModelBluePrint(tar_pcore, tar_dcore)
        self.MCores[name] = bp_abm
        return bp_abm
