from Elements import Elements

# dictionaries for Mynts text properties and numeric properties;  # todo complete list
# used to convert dave names to the corresponding Mynts properties
#
MyntsTextProps = {
    "dave_name": "name",
    "lat": "Y",
    "long": "X",
    "from_junction": "node1",
    "to_junction": "node2",
}
MyntsNumProps = {"diameter_mm": "D"}


class MyntsWriter:

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
            type = element.type
            # if type=="p":
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

    # convert prop value to Mynts internal unit				# todo complete list
    def convertPropValue2Mynts(self, prop, value) -> str:
        fvalue = float(value)
        if prop == "diameter_mm":
            fvalue = fvalue / 1.0e3
        elif prop == "length_km":
            fvalue = fvalue * 1.0e3
        # elif prop.endswith("bar"): ok
        return str(fvalue)
