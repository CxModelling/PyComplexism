from dzdy.director import *
from abc import ABCMeta, abstractmethod
import logging

__author__ = 'TimeWz667'

logger = logging.getLogger(__name__)


class UIModel:
    def __init__(self, name):
        self.Name = name
        self.PCores = dict()
        self.DCores = dict()
        self.MCores = dict()
        self.Layouts = dict()
        self.Models = dict()

    def __add_pc(self, pc):
        pass

    def __add_dc(self, dc):
        pass

    def __add_mc(self, mc):
        pass

    def __add_layout(self):
        pass

    def new_dc(self, name, dc_type):
        pass

    def renew_dc(self, name, dc_info):
        pass

    def new_mc(self, name, mc_type):
        pass

    def renew_mc(self, name, mc_info):
        pass

    def copy_mc(self, name_new, name_old):
        pass

    def new_layout(self, name, layout):
        pass

    def new_model(self, name):
        pass

    def simulate_model(self, name):
        pass

    def load_pc(self, file):
        pass

    def load_dc(self, file):
        pass

    def load_mc(self, file):
        pass

    def load_layout(self, file):
        pass

    def save(self, file):
        pass

    def save_pc(self, pc, file):
        pass

    def save_dc(self, dc, file):
        pass

    def save_mc(self, mc, file):
        pass

    def save_layout(self, ly, file):
        pass


class UIView(metaclass=ABCMeta):

    @abstractmethod
    def start(self):
        pass


class UIController:
    def __init__(self, view=None):
        self.Model = None
        self.View = view

    def start(self):
        self.View.start()

    def load(self, file):
        pass

    def handler(self, evt):
        if evt['CMD'] == '':
            pass
        else:
            logger.error('Unknown input')