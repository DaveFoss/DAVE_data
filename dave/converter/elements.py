# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.
from pandas import Series


class Element:
    """
    This class defines a single object of a net

        defines:
                 attributes: dictionary of properties of the object as string pairs key:value
                     key: the attribute's name, value: the attribute's value
                 type:       type of the attribute: n(ode) or p(ipe) or v(alve)  c(ompressor)
                 name:       name of the object

    example usage: Element(type="p", name="Pipe_1")

    """

    def __init__(self, element_type="None", name=""):
        self.attributes = {}
        self.type = element_type  # n, p, v, c, r, None
        self.name = name

    # add an attribute to the element
    def addAttribute(self, key, value):
        self.attributes[key] = value

    #   get a property from the attributes dict, return None if prop not found
    def get(self, prop):
        if prop in self.attributes:
            return self.attributes[prop]
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

    ignoreList = (
        "param",
        "uncertainty",
        "method",
        # "geometry",
        "dave_name",
    )  # attributes of dave to be ignored

    def __init__(self, element_type=None, data=None):
        self.eleList = None
        self.elements = {}  #
        self.type = "None"  # n, p, v, c, r, None
        # self.name = ""
        self.eleIndex = 0
        self.n_ele = 0
        if element_type is not None:
            self.type = element_type
        if data is not None:
            self.insert(element_type, data)

    # Get the Element with the specified name; returns None if Element not found
    def get(self, name):
        if name in self.elements:
            return self.elements[name]
        return None

    # iterator for the Elements, returns one Element after the other;  at the end None is returned
    def nextEle(self):
        name = next(self.eleList, None)
        if name is not None:
            self.eleIndex += 1
            return self.elements[name]
        # resets after full cycle
        self.eleList = iter(self.elements)
        return None

    def insert(self, element_type, data):
        """
        This function fills the dictionary with data elements from Dave;
            defines:
                         n_ele number of elements
                         type  short form for type of the Elements: n(ode) or p(ipe) or v(alve) or c(ompressor)

        INPUT:
            **element_type** (src)  -
            **data** (dict) - all Information's about the grid elements (e.g. pandas.core.series.Series)
        """
        self.type = element_type
        self.n_ele = len(data.index)
        # create dave names in case there are none
        type_names = {"p": "pipe", "v": "valve", "n": "node", "c": "compressor", "r": "regulator"}
        if not "dave_name" in data.keys():
            data.insert(
                0,
                "dave_name",
                Series(
                    list(map(lambda x: f"{type_names[element_type]}_{x}", data.index)), data.index
                ),
            )
        for ele in range(self.n_ele):
            name = data["dave_name"][ele]
            newElem = Element(element_type, name)
            for key in data.keys():
                if key not in self.ignoreList:
                    newElem.addAttribute(key, data[key][ele])
            self.elements[name] = newElem
            # print ("newElem:", newElem)
        self.eleList = iter(self.elements)
