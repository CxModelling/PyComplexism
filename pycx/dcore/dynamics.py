from abc import abstractmethod, ABCMeta
from pycx.element import Event

__author__ = 'TimeWz667'
__all__ = ['Stock', 'AbsDynamicModel', 'AbsBlueprint']


class Stock(metaclass=ABCMeta):
    def __init__(self, name, mod=None):
        """
        A static valuable of current status
        :param name: name of the stock value
        :type name: str
        :param mod: source model of this stock value
        """
        self.Name = name
        self.Model = mod

    @abstractmethod
    def next_event(self, ti=0, attr=None):
        """
        Find the next event
        :param ti: current time
        :type ti: float, int
        :param attr: external attributes for querying next events
        :type attr: dict
        :return: the nearest events
        :rtype: Event
        """
        return

    def execute(self, evt):
        """
        Find the state after transition
        :param evt: event waited for execution
        :type evt: Event
        :return: next state
        """
        return self.Model.execute(self, evt)

    def __repr__(self):
        return str(self.Name)

    def __str__(self):
        return str(self.Name)


class AbsDynamicModel(metaclass=ABCMeta):
    """
    Abstract class of dynamic model. This class and its offspring would never expose to agent
    """
    def __init__(self, name, js):
        self.__Name = name
        self.__JSON = js

    @property
    def Name(self):
        return self.__Name

    @abstractmethod
    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        return self.compose_stock(key=item)

    @abstractmethod
    def compose_stock(self, key):
        """
        Compose a stock value with a given key
        :param key:
        :return: a stock value
        :rtype: Stock
        """
        pass

    @abstractmethod
    def execute(self, st, evt):
        """
        Execute event based on state
        :param st: stock
        :type st: Stock
        :param evt: an event to be executes
        :type evt: Event
        :return: next stock value
        :rtype: Stock
        """
        pass

    def to_json(self):
        """
        Convert the model to json format
        :return: JSON form
        """
        return self.__JSON

    @abstractmethod
    def clone(self, *args, **kwargs):
        pass

    def __repr__(self):
        return str(self.to_json())


class AbsBlueprint(metaclass=ABCMeta):
    """
    A blueprint of model structure without declaring all parameters
    """
    def __init__(self, name):
        self.__Name = name

    @property
    def Name(self):
        return self.__Name

    @property
    @abstractmethod
    def RequiredSamplers(self) -> list:
        """
        Get the name of distributions required from a parameter model
        :return: list of required distributions
        :rtype: list
        """
        pass

    @abstractmethod
    def generate_model(self, name=Name, *args, **kwargs):
        """
        use a parameter core to generate a dynamic model
        :param name: name of dynamic model
        :return: a dynamic core
        """
        pass

    @abstractmethod
    def to_json(self):
        """
        Convert the model structure to json format
        :return: JSON form
        """
        pass

    def __repr__(self):
        return str(self.to_json())
