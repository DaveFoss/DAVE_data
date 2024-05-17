# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from abc import ABC, abstractmethod

from dave_client.io.file_io import from_json


# Strategy interface; used to define different output strategies dave2mynts, dave2...
class Strategy(ABC):
    @abstractmethod
    def execute(self, element_types) -> str:
        pass


class Converter:
    """
    Converter class
        defines:
                strategy        the strategy interface
                basefilepath    # basic file path for output files
                infilename        # input json file with DaVe structure data
        Example Usage:
                Converter(infilename="myDaveFile.json", basefilepath="/tmp")
    """

    strategy: Strategy
    basefilepath = ""

    def setStrategy(self, strategy: Strategy = None) -> None:
        if strategy is not None:
            self.strategy = strategy
        else:
            self.strategy = Default()

    def executeStrategy(self, element_types) -> str:
        text = self.strategy.execute(element_types)
        return text

    def __init__(self, grid_data, infilename: str = "", basefilepath: str = ""):
        if infilename:  # is not empty
            self.infilename = (
                infilename.strip()
            )  # !!! Case for read in dave_dataset.json file without generating
            self.grid_data = from_json(self.infilename)
        else:
            self.grid_data = grid_data
        if basefilepath:
            self.basefilepath = basefilepath.strip() + "/dave_mynts"
        self.initData()

    def getBasicPath(self) -> str:
        return self.basefilepath

    def setBasicPath(self, basefilepath):
        self.basefilepath = basefilepath

    # get data from Dave as nodes, pipes and valves  # !!! todo: other components if there are any
    def initData(self):
        self.nodedata = self.grid_data.hp_data.hp_junctions  # nodes
        self.pipedata = self.grid_data.hp_data.hp_pipes  # pipes
        self.valvedata = self.grid_data.components_gas.valves
        self.compressordata = self.grid_data.components_gas.compressors  #
        self.sinkdata = self.grid_data.components_gas.sinks  #
        self.sourcedata = self.grid_data.components_gas.sources  #
        self.nvalves = len(self.valvedata.index)
        self.npipes = len(self.pipedata.index)
        self.nnodes = len(self.nodedata.index)
        self.ncompressors = len(self.compressordata.index)
        self.nsinks = len(self.sinkdata.index)
        self.nsources = len(self.sourcedata.index)
        # print("Read ", self.nnodes, " nodes", self.npipes, " pipes", self.nvalves, "valves")
        # self.nodeElements = iter(self.nodedata)

        print("\n")
        print(str(self.nnodes) + " nodes extracted from DaVe")
        print(str(self.nsinks) + " sinks extracted from DaVe")
        print(str(self.nsources) + " sources extracted from DaVe")
        print(str(self.npipes) + " pipes extracted from DaVe")
        print(str(self.nvalves) + " valves extracted from DaVe")
        print(str(self.ncompressors) + " compressors extracted from DaVe")

    def getAllData(self):
        all_data = self.nodedata
        all_data.append(self.pipedata)
        all_data.append(self.valvedata)
        all_data.append(self.compressordata)
        all_data.append(self.sinkdata)
        all_data.append(self.sourcedata)
        return all_data


class Default(Strategy):
    def execute(self, element_types=None) -> str:
        return "Default"
