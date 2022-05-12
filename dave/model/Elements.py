class Element:
    """
    This class defines a single object of a net

        defines:
                 attributes: dictionary of properties of the object as string pairs key:value
                     key: the attribute's name, value: the attribute's value
                 type:       type of the attribute: n(ode) or p(ipe) or v(alve)
                 name:       name of the object

    example usage: Element(type="p", name="Pipe_1")

    """

    def __init__(self, type="None", name=""):
        self.attributes = {}
        self.type = type  # n, p, v, None
        self.name = name

    # add an attribute to the element
    def addAttribute(self, key, value):
        self.attributes[key] = value

    #   get a property from the attributes dict, return None if prop not found
    def get(self, prop):
        if prop in self.attributes:
            return self.attributes[prop]
        else:
            return None

    # iterator for the attributes, returns one attribute after the other, at the end None is returned
    def props(self):
        attrList = iter(self.attributes)
        n = 0
        while n < len(self.attributes):
            yield next(attrList)
            n += 1


class Elements:
    """
    This class defines a dictionary of objects of a net as Element objects of a single type
    """

    ignoreList = ("param", "uncertainty", "method")  # attributes of dave to be ignored

    def __init__(self, type=None, data=None):
        self.elements = {}  #
        self.type = "None"  # n, p, v, None
        # self.name = ""
        self.eleIndex = 0
        self.n_ele = 0
        if type is not None:
            self.type = type
        if data is not None:
            self.insert(type, data)

    # Get the Element with the specified name; returns None if Element not found
    def get(self, name) -> Element:
        if name in self.elements:
            return self.elements[name]
        else:
            return None

    # iterator for the Elements, returns one Element after the other;  at the end None is returned
    def nextEle(self) -> str:
        self.eleIndex += 1
        if self.eleIndex < self.n_ele:
            name = next(self.eleList)
            return self.elements[name]
        else:
            return None

    """
    This function fills the dictionary with data elements from Dave;
        defines:
			 n_ele number of elements
			 type  short form for type of the Elements: n(ode) or p(ipe) or v(alve)

    INPUT:
        **type** (src)  - 
        **data** (dict) - all Informations about the grid elements (e.g. pandas.core.series.Series)
    """

    def insert(self, type, data):
        self.type = type
        self.n_ele = len(data.index)
        for ele in range(0, self.n_ele):
            name = data["dave_name"][ele]
            newElem = Element(type, name)
            for key in data.keys():
                if key not in self.ignoreList:
                    newElem.addAttribute(key, data[key][ele])
            self.elements[name] = newElem
            # print ("newElem:", newElem)
        self.eleList = iter(self.elements)
