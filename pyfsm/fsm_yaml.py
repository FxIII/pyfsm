import yaml
from pyfsm import FSM

class yamlFSM(FSM):
    def __init__(self):
        descr = yaml.load(self.__doc__)
        descr["handlers"] = dict(
            (i,getattr(self.__class__,i))
            for i in dir(self.__class__) if not i.startswith("_"))
        FSM.__init__(self,descr)

