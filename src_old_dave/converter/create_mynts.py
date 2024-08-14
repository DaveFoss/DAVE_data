# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dave.converter.converter import Converter
from dave.converter.converter import Strategy
from dave.converter.elements import Elements
from dave.settings import dave_settings
from tqdm import tqdm

# dictionaries for Mynts text properties and numeric properties;  # !!! todo complete list
# used to convert dave names to the corresponding Mynts properties

MyntsTextProps = {
    "dave_name": "name",
    "lat": "Y",
    "long": "X",
    "from_junction": "node1",
    "to_junction": "node2",
    "country_code": "Des",
    "scigrid_name": "Bez",
    "junction": "node",
}

MyntsNumProps = {
    "diameter_mm": "D",
    "length_km": "L",
    "height_m": "H",
    "roughness": "k",
    "max_pressure_bar": "POMAX",
}

MyntsReqNodeProps = [
    "H",
    "X",
    "Y",
    "Web",
    "KTyp",
    "nVNB",
    "aFNB",
    "EIC",
    "MG",
    "Zuornd",
    "Des",
    "GeoLat",
    "GeoLong",
    "AnLNum",
    "LNum",
    "Schemaplan",
    "UmstSchr",
    "UmstTag",
    "NEPID",
    "NEPID18",
    "UmstJ",
    "UmstBer",
    "Zone",
    "Teilnetz",
    "Messort",
]


MyntsReqPipeProps = [
    "node1",
    "node2",
    "L",
    "D",
    "k",
    "htc",
    "NurPlan",
    "Bez",
    "Des",
    "LNum",
    "LName",
    "PNPipe",
    "Eig",
    "NEPID",
    "NEPID18",
    "UmstJ",
    "ModVar",
    "IJahr",
    "UmstBer",
    "UmstSchr",
    "UmstTag",
    "Update",
]

MyntsReqValveProps = [
    "node1",
    "node2",
    "pimin",
    "pomax",
    "L",
    "D",
    "NurPlan",
    "Bez",
    "Des",
    "LNum",
    "LName",
    "Autom",
    "Eig",
    "NEPID",
    "NEPID18",
    "UmstJ",
    "ModVar",
    "IJahr",
    "UmstSchr",
    "Update",
]

MyntsReqCompressorProps = [
    "D",
    "pimin",
    "pomax",
    "node1",
    "node2",
    "kind",
    "NurPlan",
    "Bez",
    "Des",
    "Autom",
    "Eig",
    "NEPID",
    "NEPID18",
    "UmstJ",
    "ModVar",
    "IJahr",
    "UmstSchr",
    "Update",
]

MyntsReqDriveProps = [
    "node",
    "kind",
    "NurPlan",
    "Bez",
    "Des",
    "Autom",
    "Eig",
    "NEPID",
    "NEPID18",
    "UmstJ",
    "ModVar",
    "IJahr",
    "UmstSchr",
    "Update",
]

MyntsReqProps = {
    "n": MyntsReqNodeProps,
    "p": MyntsReqPipeProps,
    "v": MyntsReqValveProps,
    "c": MyntsReqCompressorProps,
    "d": MyntsReqDriveProps,
}


# convert prop value to Mynts internal unit                # !!! todo complete list
def convertPropValue2Mynts(prop, value) -> str:
    #    if prop=="roughness":
    #        print("roughness ="+str(value))
    if value == "":
        return "-1"
    fvalue = float(value)
    if prop == "diameter_mm":
        fvalue = fvalue / 1.0e3
    elif prop == "length_km":
        fvalue = fvalue * 1.0e3
    # elif prop.endswith("bar"): ok
    return str(fvalue)


# get Mynts name of DaVe property; returns original name if not in Mynts name dict
def myntsProp(prop) -> str:
    if prop in MyntsTextProps:
        return MyntsTextProps[prop]
    elif prop in MyntsNumProps:
        return MyntsNumProps[prop]
    return prop


def daveProp(prop) -> str:
    # reversed MyntsProp dict lists
    daveProps = {y: x for x, y in MyntsTextProps.items()}
    daveNumProps = {y: x for x, y in MyntsNumProps.items()}
    if prop in daveProps:
        return daveProps[prop]
    if prop in daveNumProps:
        return daveNumProps[prop]
    return prop


class MyntsWriter:  # Output file strategy class for Mynts
    elements = Elements()
    MyntsProps = {}

    def __init__(self, file=None):
        self.file = file

    def setFile(self, file):
        self.file = file

    # get the elements from Elements dict and write to geom file
    def writeGeom(self, elements):
        self.elements = elements
        element = elements.nextEle()
        while element is not None:
            self.writeGeomElement(element)
            element = elements.nextEle()

    # get the elements from Elements dict and write to scen file
    def writeScen(self, elements):
        self.elements = elements
        element = elements.nextEle()
        while element is not None:
            self.writeScenElement(element)
            element = elements.nextEle()

    def writeGeomHeader(self):
        line = '{"#MYNTS_GEOM":"Base topology file ' + self.file.name + '"\n'
        self.file.write(line)

    def writeScenHeader(self):
        line = '{"#MYNTS_SCEN":"Scenario ' + self.file.name + '"\n'
        self.file.write(line)

    def writeFooter(self):
        self.file.write("}\n")

    # write an element in geom format
    def writeGeomElement(self, element):
        line = ',"' + element.name + '":{"obj_type":"' + element.type + '"'
        #
        for prop in MyntsReqProps[element.type]:
            dave_prop = daveProp(prop)
            newValue = str(element.get(dave_prop))
            # write required text Props even without a value
            if element.get(dave_prop) is None:
                newValue = ""
            # convert numeric value and ignore if it has no value
            if dave_prop in MyntsNumProps:
                if convertPropValue2Mynts(dave_prop, newValue) == "-1":
                    continue
                newValue = convertPropValue2Mynts(dave_prop, newValue)
            if element.name.startswith("sink") and dave_prop == "lat":
                newValue = str(element.get(dave_prop) - 0.01)
            if element.name.startswith("source") and dave_prop == "lat":
                newValue = str(element.get(dave_prop) + 0.01)
            line = line + ', "' + prop + '":"' + newValue + '"'
        line = line + "}\n"
        self.file.write(line)
        if element.name.startswith("sink") or element.name.startswith(
            "source"
        ):
            line = ',"s_' + element.name + '":{"obj_type":"s"'
            line = line + ', "node1":"' + element.get("junction") + '"'
            line = line + ', "node2":"' + element.name + '"'
            line = line + "}\n"
            self.file.write(line)

    # write an element in scen format
    def writeScenElement(self, element):
        line = ',"' + element.name + '":{'
        #
        first_element = True
        for prop in element.props():
            newName = myntsProp(prop)
            newValue = str(element.get(prop))
            if (
                newName.casefold()
                in (prop.casefold() for prop in MyntsReqProps[element.type])
                or element.get(prop) is None
            ):
                continue
            if prop in MyntsNumProps:
                newValue = convertPropValue2Mynts(prop, newValue)
            if first_element:
                line = line + '"' + newName + '":"' + newValue + '"'
                first_element = False
                continue
            line = line + ', "' + newName + '":"' + newValue + '"'
        line = line + "}\n"
        self.file.write(line)


class DaVe2Mynts(Strategy):
    """
    class to convert dave data to Mynts output files, one for each format
    """

    def __init__(self, basefilepath):
        self.files = {}
        self.writer = None
        self.basefilepath = basefilepath
        self.openFiles(self.basefilepath)

    def __del__(self):
        for file in self.files.keys():
            self.files[file].close()

    # opens a file for each output format
    def openFiles(self, outfile):
        self.files["geom"] = open(outfile + ".geom.jsn", "w")
        self.files["scen"] = open(outfile + ".scen.jsn", "w")
        self.writer = MyntsWriter()

    # writes elements to geom and scen
    def execute(self, element_types) -> str:
        # write elements in geom file
        self.writer.setFile(self.files["geom"])
        self.writer.writeGeomHeader()
        for elements in element_types:
            self.writer.writeGeom(elements)
        self.writer.writeFooter()
        # write elements in scen file
        self.writer.setFile(self.files["scen"])
        self.writer.writeScenHeader()
        for elements in element_types:
            self.writer.writeScen(elements)
        self.writer.writeFooter()
        return "DaVe2Mynts"


def create_mynts(grid_data, output_folder, idx_ref="dave_name"):
    """
    This function creates a network in MYNTS format based of an DAVE dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from DAVE
        **output_folder** (str) - patht to the location where the results will be saved

    OPTIONAL:
        **idx_ref** (str, default='dave_name') - defines parameter which should use as referenz \
            for setting the indices

    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create mynts network:              ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )

    # seperate geocoordinates from geometry parameter into lat and long
    grid_data.hp_data.hp_junctions["long"] = (
        grid_data.hp_data.hp_junctions.geometry.apply(lambda x: x.x)
    )
    grid_data.hp_data.hp_junctions["lat"] = (
        grid_data.hp_data.hp_junctions.geometry.apply(lambda x: x.y)
    )
    # init data
    myntsconv = Converter(
        grid_data, basefilepath=output_folder
    )  # default file names
    # update progress
    pbar.update(50)
    print()

    # extract the data from DaVe
    nodes = Elements("n", myntsconv.nodedata)
    sinks = Elements("n", myntsconv.sinkdata)
    sources = Elements("n", myntsconv.sourcedata)
    pipes = Elements("p", myntsconv.pipedata)  # stores all pipe elements
    valves = Elements("v", myntsconv.valvedata)
    compressors = Elements("c", myntsconv.compressordata)
    ###drives = Elements("d", myntsconv.compressordata)
    # update progress
    pbar.update(25)

    # init writing to Mynts geom.jsn file
    output_folder = myntsconv.getBasicPath()  # basic output file path
    myntsconv.setStrategy(DaVe2Mynts(output_folder))  # define Strategy

    # fixed order to write the elements
    ###all_elements = [nodes, sinks, sources, pipes, valves, compressors, drives]
    all_elements = [nodes, sinks, sources, pipes, valves, compressors]

    myntsconv.executeStrategy(all_elements)
    # print(text, ": ", ele_type.type, " written to Mynts Geom")
    # update progress
    pbar.update(25)
