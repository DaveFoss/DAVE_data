__version__ = "0.1"

# import fileinput

import sys
from abc import ABC, abstractmethod

from Elements import Elements

import dave.io as dio


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

    def __init__(self, infilename: str = "", basefilepath: str = ""):
        if infilename:  # is not empty
            self.infilename = infilename.strip()
        else:  # for testing
            self.infilename = "/home/cass/TransHyDE/DaVe/dave_dataset_valves.json"
        if basefilepath:
            self.basefilepath = basefilepath.strip()
        else:
            self.basefilepath = "/tmp/dave2Mynts.geom"  # for testing
        print("Read from file ", self.infilename)

    def getBasicPath(self) -> str:
        return self.basefilepath

    def setBasicPath(self, basefilepath):
        self.basefilepath = basefilepath

    # get data from Dave as nodes, pipes and valves 	#todo: other components like compressors etc
    def getData(self):
        grid_data = dio.from_json(self.infilename)
        gas_data = grid_data.components_gas
        hp_data = grid_data.hp_data
        # print (hp_data)  for testing
        self.nodedata = grid_data.hp_data.hp_junctions  #
        # print (self.nodedata)
        self.pipedata = grid_data.hp_data.hp_pipes  # pipes
        self.valvedata = grid_data.components_gas.valves
        self.compressors = gas_data.compressors  #
        self.nvalves = len(self.valvedata.index)
        self.npipes = len(self.pipedata.index)
        self.nnodes = len(self.nodedata.index)
        # print ("Read ", nnodes, " nodes", npipes, " pipes", nvalves, "valves", " from file ", self.filename)
        # self.nodeElements = iter(self.nodedata)


from MyntsWriter import MyntsWriter  # Output file strategy class for Mynts


class DaVe2Mynts(Strategy):
    """
    class to convert dave data to Mynts output files, one for each format
    """

    files = {}
    fileformat = ["jsn"]  # ,'netlist', ...
    format = ""  # format of the output file data
    writer = {}  # writers for each form

    def __init__(self, basefilepath):
        self.basefilepath = basefilepath
        self.openFiles(self.basefilepath)

    def __del__(self):
        for form in self.fileformat:
            self.writer[form].writeFooter()
            self.files[form].close()

    # opens a file for each output format
    def openFiles(self, outfile):
        for form in self.fileformat:
            if form == "netlist":
                filename = outfile
            else:
                filename = outfile + "." + form
            file = open(filename, "w")
            self.files[form] = file
            print("opened file ", file.name)
            self.writer[form] = MyntsWriter(form=form, file=file)

    def execute(self, elements) -> str:
        for form in self.fileformat:
            self.writer[form].writeGeom(elements)
        return "DaVe2Mynts"

    def setForm(self, format):
        self.format = format


class Default(Strategy):
    def execute(self, elements=None) -> str:
        return "Default"


"""
Example usage 
"""
myntsconv = Converter()  # default file names
myntsconv.getData()  # gets data from DaVe input file

# extract the data from DaVe
pipes = Elements()
pipes.insert("p", myntsconv.pipedata)  # stores all pipe elements
print(myntsconv.npipes, " pipes\n")

valves = Elements("v", myntsconv.valvedata)
nodes = Elements("n", myntsconv.nodedata)

# init writing to Mynts geom.jsn file
basefilepath = myntsconv.getBasicPath()  # basic output file path
print("basic path is ", basefilepath)
myntsconv.setStrategy(DaVe2Mynts(basefilepath))  # define Strategy

eletypes = [nodes, pipes, valves]  # only those now available
for eletype in eletypes:
    text = myntsconv.executeStrategy(eletype)
    print(text, ": ", eletype.type, " written to Mynts Geom")
