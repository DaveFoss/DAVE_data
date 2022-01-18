import numpy as np
import pandas as pd
from lxml import etree
from tqdm import tqdm

from dave import __version__
from dave.settings import dave_settings


def create_romo(grid_data, api_use, output_folder):
    """
    This function creates a romo network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:

    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create romo model:                 ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )

    # define network
    nsm = {
        None: "http://gaslib.zib.de/Gas",
        "framework": "http://gaslib.zib.de/Framework",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    network = etree.Element("network", nsmap=nsm)
    network.attrib[
        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
    ] = "http://gaslib.zib.de/Gas Gas.xsd"
    information = etree.Element("{http://gaslib.zib.de/Framework}information")
    nodes = etree.Element("{http://gaslib.zib.de/Framework}nodes")
    connections = etree.Element("{http://gaslib.zib.de/Framework}connections")

    # create informations
    # !!! Todo: Noch eintragen Titel, region, DaVe Version ....
    information.attrib["title"] = ""
    information.attrib["area"] = ""
    information.attrib["grid_levels"] = str(grid_data.target_input.gas_levels.iloc[0])
    information.attrib["dave_version"] = __version__

    # --- create nodes
    nodes_dave = grid_data.hp_data.hp_junctions
    # !!! umändern zu den SCiGridGas Daten
    nodes_dave.insert(
        0,
        "is_export",
        pd.Series(list(map(lambda x: np.random.randint(2), nodes_dave.index))),
    )
    nodes_dave.insert(
        0,
        "is_import",
        pd.Series(list(map(lambda x: np.random.randint(2), nodes_dave.index))),
    )
    nodes_dave["elevation_m"] = 1

    # Fall export, import
    # Fall 0,0 => innerer Knoten (Verbindung)
    # Fall 0,1 => Quelle
    # Fall 1,0 => Senke
    # Fall 1,1 => Quelle und Senke
    for _, node in nodes_dave.iterrows():
        #

        if (node.is_export == 0 and node.is_import == 0) or (
            node.is_export == 1 and node.is_import == 1
        ):
            innode = etree.Element("innode", {"alias": "", "y": "", "x": ""})
            innode.attrib["geoWGS84Long"] = str(node.long)
            innode.attrib["geoWGS84Lat"] = str(node.lat)
            innode.attrib["id"] = f"innode_{node.dave_name}"
            innode_id = f"innode_{node.dave_name}"
            height = etree.Element("height")
            height.attrib["unit"] = "m"
            height.attrib["value"] = str(node.elevation_m)
            innode.append(height)
            etree.SubElement(
                innode, "presssureMin", {"unit": "bar", "value": "1.0"}
            )  # !!! Todos rauslesen aus pipes min max
            etree.SubElement(
                innode, "presssureMax", {"unit": "bar", "value": "100.0"}
            )  # !!! Todos rauslesen aus pipes min max
            nodes.append(innode)

        if (node.is_export == 0 and node.is_import == 1) or (
            node.is_export == 1 and node.is_import == 1
        ):

            source = etree.Element("source", {"alias": "", "y": "", "x": ""})
            source.attrib["geoWGS84Long"] = str(node.long)
            source.attrib["geoWGS84Lat"] = str(node.lat)
            source.attrib["id"] = f"source_{node.dave_name}"
            source_id = f"source_{node.dave_name}"

            height = etree.Element("height")
            height.attrib["unit"] = "m"
            height.attrib["value"] = str(node.elevation_m)
            source.append(height)

            etree.SubElement(
                source, "presssureMin", {"unit": "bar", "value": "1.0"}
            )  # !!! Todos rauslesen aus pipes min max
            etree.SubElement(
                source, "presssureMax", {"unit": "bar", "value": "100.0"}
            )  # !!! Todos rauslesen aus pipes min max
            etree.SubElement(
                source, "flowMin", {"unit": "1000m_cube_per_hour", "value": "0"}
            )  # !!! annahme
            etree.SubElement(
                source, "flowMax", {"unit": "1000m_cube_per_hour", "value": "10000"}
            )  # !!! annahme
            etree.SubElement(
                source, "gasTemperature", {"unit": "Celsius", "value": "15"}
            )  # !!! annahme
            etree.SubElement(
                source, "calorificValue", {"unit": "MJ_per_m_cube", "value": "41.342270292"}
            )  # !!! annahme
            etree.SubElement(
                source, "normDensity", {"unit": "kg_per_m_cube", "value": "0.82"}
            )  # !!! annahme
            etree.SubElement(
                source, "coefficient-A-heatCapacity", {"value": "31.61010551"}
            )  # !!! annahme
            etree.SubElement(
                source, "coefficient-B-heatCapacity", {"value": "-0.004284754861"}
            )  # !!! annahme
            etree.SubElement(
                source, "coefficient-C-heatCapacity", {"value": "8.019089e-05"}
            )  # !!! annahme
            etree.SubElement(
                source, "molarMass", {"unit": "kg_per_kmol", "value": "18.0488790169"}
            )  # !!! annahme
            etree.SubElement(
                source, "pseudocticticalPressure", {"unit": "bar", "value": "46.7020607"}
            )  # !!! annahme
            etree.SubElement(
                source, "pseudocticticalTemperature", {"unit": "K", "value": "202.4395142"}
            )  # !!! annahme
            nodes.append(source)

        if (node.is_export == 1 and node.is_import == 0) or (
            node.is_export == 1 and node.is_import == 1
        ):
            sink = etree.Element("sink", {"alias": "", "y": "", "x": ""})
            sink.attrib["geoWGS84Long"] = str(node.long)
            sink.attrib["geoWGS84Lat"] = str(node.lat)
            sink.attrib["id"] = f"sink_{node.dave_name}"
            sink_id = f"sink_{node.dave_name}"
            etree.SubElement(
                sink, "presssureMin", {"unit": "bar", "value": "1.0"}
            )  # !!! Todos rauslesen aus pipes min max
            etree.SubElement(
                sink, "presssureMax", {"unit": "bar", "value": "100.0"}
            )  # !!! Todos rauslesen aus pipes min max
            etree.SubElement(
                sink, "flowMin", {"unit": "1000m_cube_per_hour", "value": "0"}
            )  # !!! annahme
            etree.SubElement(
                sink, "flowMax", {"unit": "1000m_cube_per_hour", "value": "10000"}
            )  # !!! annahme
            height = etree.Element("height")
            height.attrib["unit"] = "m"
            height.attrib["value"] = str(node.elevation_m)
            sink.append(height)
            nodes.append(sink)

        if node.is_export == 1 and node.is_import == 1:

            # da quelle und senke macht man zwei short pipes um diese voneinander zu unterscheiden
            short_pipe_sink = etree.Element("shortPipe")
            short_pipe_sink.attrib["alias"] = ""
            short_pipe_sink.attrib["id"] = f"short_pipe_{sink_id}_{innode_id}"
            short_pipe_sink.attrib["from"] = sink_id
            short_pipe_sink.attrib["to"] = innode_id
            etree.SubElement(
                short_pipe_sink, "flowMin", {"unit": "1000m_cube_per_hour", "value": "-10000"}
            )  # !!! annahme
            etree.SubElement(
                short_pipe_sink, "flowMax", {"unit": "1000m_cube_per_hour", "value": "10000"}
            )  # !!! annahme
            connections.append(short_pipe_sink)

            short_pipe_source = etree.Element("shortPipe")
            short_pipe_source.attrib["alias"] = ""
            short_pipe_source.attrib["id"] = f"short_pipe_{source_id}_{innode_id}"
            short_pipe_source.attrib["from"] = source_id
            short_pipe_source.attrib["to"] = innode_id
            etree.SubElement(
                short_pipe_source, "flowMin", {"unit": "1000m_cube_per_hour", "value": "-10000"}
            )  # !!! annahme
            etree.SubElement(
                short_pipe_source, "flowMax", {"unit": "1000m_cube_per_hour", "value": "10000"}
            )  # !!! annahme
            connections.append(short_pipe_source)

    # create connections

    # save pandapower model in the dave output folder
    # if not api_use:
    #     file_path = output_folder + "\\dave_romo.json"
    #     pp_to_json(net, file_path)
    # return net
