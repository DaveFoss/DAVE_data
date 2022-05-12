from tqdm import tqdm

from dave.model.converter import Converter, Strategy
from dave.model.elements import Elements
from dave.settings import dave_settings

# dictionaries for Mynts text properties and numeric properties;  # !!! todo complete list
# used to convert dave names to the corresponding Mynts properties

MyntsTextProps = {
    "dave_name": "name",
    "lat": "Y",
    "long": "X",
    "from_junction": "node1",
    "to_junction": "node2",
}
MyntsNumProps = {"diameter_mm": "D"}


class MyntsWriter:  # Output file strategy class for Mynts

    elements = Elements()
    MyntsProps = {}

    def __init__(self, form="", file=None):
        self.file = file
        self.form = form
        self.writeHeader()

    def __del__(self):
        # self.writeFooter()
        pass

    def setFile(self, file):
        self.file = file
        self.writeHeader()

    def setForm(self, form):
        self.form = form

    # get the elements from Elements dict and write to file
    def writeGeom(self, elements):
        self.elements = elements
        element = elements.nextEle()
        while element is not None:
            element_type = element.type
            # if element_type=="p":
            #     self.writePipe(element)
            self.writeElement(element)
            # else
            element = elements.nextEle()

    def writeHeader(self):
        line = '{"#MYNTS_GEOM":"Base topology file "' + self.file.name + '"\n'
        self.file.write(line)

    def writeFooter(self):
        self.file.write("}\n")

    def writeElement(self, element):
        line = ',"' + element.name + '":{"obj_type":"' + element.type + '"'
        #
        for prop in element.props():
            newName = self.myntsProp(prop)
            newvalue = str(element.get(prop))

            if prop in MyntsNumProps:
                newvalue = self.convertPropValue2Mynts(prop, newvalue)
            line = line + ', "' + newName + '":"' + newvalue + '"'
        line = line + "}\n"
        self.file.write(line)

    # get Mynts name of DaVe property; returns original name if not in Mynts name dict
    def myntsProp(self, prop) -> str:
        if prop in MyntsTextProps:
            return MyntsTextProps[prop]
        elif prop in MyntsNumProps:
            return MyntsNumProps[prop]
        else:
            return prop

    # convert prop value to Mynts internal unit				# !!! todo complete list
    def convertPropValue2Mynts(self, prop, value) -> str:
        fvalue = float(value)
        if prop == "diameter_mm":
            fvalue = fvalue / 1.0e3
        elif prop == "length_km":
            fvalue = fvalue * 1.0e3
        # elif prop.endswith("bar"): ok
        return str(fvalue)


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
            self.writer[form] = MyntsWriter(form=form, file=file)

    def execute(self, elements) -> str:
        for form in self.fileformat:
            self.writer[form].writeGeom(elements)
        return "DaVe2Mynts"

    def setForm(self, format):
        self.format = format


def create_mynts(grid_data, basefilepath):
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create mynts network:              ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )

    myntsconv = Converter(grid_data, basefilepath=basefilepath)  # default file names
    myntsconv.getData()  # gets data from DaVe input file
    # update progress
    pbar.update(50)

    # extract the data from DaVe
    pipes = Elements()
    pipes.insert("p", myntsconv.pipedata)  # stores all pipe elements
    valves = Elements("v", myntsconv.valvedata)
    nodes = Elements("n", myntsconv.nodedata)
    # update progress
    pbar.update(25)

    # init writing to Mynts geom.jsn file
    basefilepath = myntsconv.getBasicPath()  # basic output file path
    myntsconv.setStrategy(DaVe2Mynts(basefilepath))  # define Strategy (kann dann auch andere sein)

    eletypes = [nodes, pipes, valves]  # only those now available

    """
    # print written data to mynts file
    for eletype in eletypes:
        text = myntsconv.executeStrategy(eletype)
        print(text, ": ", eletype.type, " written to Mynts Geom")
    """
    # update progress
    pbar.update(25)
