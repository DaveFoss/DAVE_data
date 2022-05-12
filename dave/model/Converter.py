from abc import ABC, abstractmethod

from dave.io import from_json


# Strategy interface; used to define different output strategies dave2mynts, dave2...
class Strategy(ABC):
    @abstractmethod
    def execute(self, elements) -> str:
        pass


class Converter:
    """
    Converter class
        defines:
                strategy		the strategy interface
                files
                basefilepath	# basic file path for output files
                infilename		# input json file with DaVe structure data
        Example Usage:
                Converter(infilename="myDaveFile.json", basefilepath="/tmp"
    """

    strategy: Strategy
    files = {}  #
    basefilepath = ""

    def setStrategy(self, strategy: Strategy = None) -> None:
        if strategy is not None:
            self.strategy = strategy
        else:
            self.strategy = Default()

    def executeStrategy(self, elements) -> str:
        text = self.strategy.execute(elements)
        return text

    def __init__(self, grid_data, infilename: str = "", basefilepath: str = ""):
        if infilename:  # is not empty
            self.infilename = (
                infilename.strip()
            )  # !!! Case for read in dave_dataset.json file without generating
            print("Read from file ", self.infilename)
            self.grid_data = from_json(self.infilename)
        else:
            self.grid_data = grid_data
        if basefilepath:
            self.basefilepath = basefilepath.strip() + "\\dave_mynts"

    def getBasicPath(self) -> str:
        return self.basefilepath

    def setBasicPath(self, basefilepath):
        self.basefilepath = basefilepath

    # get data from Dave as nodes, pipes and valves 	# !!! todo: other components like compressors etc
    def getData(self):
        self.nodedata = self.grid_data.hp_data.hp_junctions  #
        self.pipedata = self.grid_data.hp_data.hp_pipes  # pipes
        self.valvedata = self.grid_data.components_gas.valves
        self.compressors = self.grid_data.components_gas.compressors  #
        self.nvalves = len(self.valvedata.index)
        self.npipes = len(self.pipedata.index)
        self.nnodes = len(self.nodedata.index)
        # print ("Read ", nnodes, " nodes", npipes, " pipes", nvalves, "valves", " from file ", self.filename)
        # self.nodeElements = iter(self.nodedata)


class Default(Strategy):
    def execute(self, elements=None) -> str:
        return "Default"
