# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from os.path import dirname
from os.path import join
from os.path import realpath

from xmlschema import XMLSchema


def read_gaslib_cs():
    """
    This function reads informations about gaslib compressor stations as reference for the converter
    """
    filepath = dirname(realpath(__file__))

    # read data from datapool
    schema = XMLSchema(join(filepath, "gaslib/CompressorStations.xsd"))
    gaslib_dict_cs = schema.to_dict(join(filepath, "gaslib/GasLib-582-v2.cs"))
    # create data dictionary
    gaslib_data_cs = {
        "compressor_station": gaslib_dict_cs["framework:compressorStation"]
    }
    # read meta data  # TODO: evt aus net nehmen
    # meta_data = gaslib_dict["framework:information"]

    from lxml import etree as ET

    # gaslib_data_cs_xml = etree.iterparse(get_data_path("gaslib/GasLib-582-v2.cs", "data"))
    # root = etree.parse(get_data_path("gaslib/GasLib-582-v2.cs", "data"))
    # import xml.etree.ElementTree as ET

    tree = ET.parse(join(filepath, "gaslib/GasLib-582-v2.cs"))
    gaslib_data_cs_xml = tree.getroot()

    return gaslib_data_cs, gaslib_data_cs_xml
