import xml.etree.ElementTree as ET

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point


def read_simone(filepath, crs="epsg:4326"):  # !!! noch ersetzen gegen filepath
    """
    This function reads given simone files in the xml format
    """
    # read data from xml
    data_nodes = {}
    data_pipes = {}
    data_compressor = {}
    data_valve = {}
    root = ET.parse(f"{filepath}.xml").getroot()
    for child in root:
        # create dict for nodes
        if child.tag == "NODES":
            for elm in child:
                data_nodes[elm.attrib["id"]] = {
                    "source_name": elm.attrib["name"],
                    "type": elm.attrib["alias"] if len(elm.attrib["alias"]) > 0 else float("nan"),
                    "geometry": Point(float(elm.attrib["x"]), float(elm.attrib["y"])),
                    "height_m": float(elm.attrib["height"]),
                    "source_id": elm.attrib[
                        "id"
                    ],  # => das dann auch bei scigrid machen, damit man einheitliches naming hat
                    "source": "SIMONE",
                    "supply": 1 if "supply" in elm.attrib else 0,
                }  # !!! supply noch abändern das es nicht als parameter steht

        # create dict for all elements that are not a node
        elif child.tag == "ELEMENTS":
            for elm in child:
                # create pipe elements
                if elm.attrib["type"] == "pipe":
                    data_pipes[elm.attrib["id"]] = {
                        "from_junction": elm[0].attrib["id"],
                        "to_junction": elm[1].attrib["id"],
                        "source_name": elm.attrib["name"],
                        "type": elm.attrib["alias"]
                        if len(elm.attrib["alias"]) > 0
                        else float("nan"),
                        "pwm": elm.attrib["pwm"],
                        "dm": elm.attrib["dm"],
                        "pwp": elm.attrib["pwp"],
                        "roughness_mm": float(elm.attrib["roughness"])
                        if elm.attrib["roughness_unit"] == "mm"
                        else f"{elm.attrib['roughness']}_{elm.attrib['roughness_unit']}",
                        "diameter_mm": float(elm.attrib["diameter"])
                        if elm.attrib["diameter_unit"] == "mm"
                        else f"{elm.attrib['diameter']}_{elm.attrib['diameter_unit']}",
                        "length_km": float(elm.attrib["length"])
                        if elm.attrib["length_unit"] == "km"
                        else f"{elm.attrib['length']}_{elm.attrib['length_unit']}",
                        "source_id": elm.attrib["id"],
                        "source": "SIMONE",
                        "geometry": LineString(
                            [
                                data_nodes[elm[0].attrib["id"]]["geometry"],
                                data_nodes[elm[1].attrib["id"]]["geometry"],
                            ]
                        ),
                    }
                # create compressor station elements
                elif elm.attrib["type"] == "compressor station":
                    data_compressor[elm.attrib["id"]] = {
                        "from_junction": elm[0].attrib["id"],
                        "to_junction": elm[1].attrib["id"],
                        "source_name": elm.attrib["name"],
                        "type": elm.attrib["alias"]
                        if len(elm.attrib["alias"]) > 0
                        else float("nan"),
                        "Rin": elm.attrib["Rin"],
                        "PIMin": elm.attrib["PIMin"],
                        "Rout": elm.attrib["Rout"],
                        "POMax": elm.attrib["POMax"],
                        "pwm": elm.attrib["pwm"],
                        "dm": elm.attrib["dm"],
                        "pwp": elm.attrib["pwp"],
                        "diameter_mm": float(elm.attrib["diameter"])
                        if elm.attrib["diameter_unit"] == "mm"
                        else f"{elm.attrib['diameter']}_{elm.attrib['diameter_unit']}",
                        "source_id": elm.attrib["id"],
                        "source": "SIMONE",
                    }
                # create compressor station elements
                elif elm.attrib["type"] == "compressor station":
                    data_compressor[elm.attrib["id"]] = {
                        "from_junction": elm[0].attrib["id"],
                        "to_junction": elm[1].attrib["id"],
                        "source_name": elm.attrib["name"],
                        "type": elm.attrib["alias"]
                        if len(elm.attrib["alias"]) > 0
                        else float("nan"),
                        "Rin": elm.attrib["Rin"],
                        "PIMin": elm.attrib["PIMin"],
                        "Rout": elm.attrib["Rout"],
                        "POMax": elm.attrib["POMax"],
                        "pwm": elm.attrib["pwm"],
                        "dm": elm.attrib["dm"],
                        "pwp": elm.attrib["pwp"],
                        "diameter_mm": float(elm.attrib["diameter"])
                        if elm.attrib["diameter_unit"] == "mm"
                        else f"{elm.attrib['diameter']}_{elm.attrib['diameter_unit']}",
                        "source_id": elm.attrib["id"],
                        "source": "SIMONE",
                    }
                # create valve elements
                elif elm.attrib["type"] == "valve":
                    data_valve[elm.attrib["id"]] = {
                        "from_junction": elm[0].attrib["id"],
                        "to_junction": elm[1].attrib["id"],
                        "source_name": elm.attrib["name"],
                        "type": elm.attrib["alias"]
                        if len(elm.attrib["alias"]) > 0
                        else float("nan"),
                        "pwm": elm.attrib["pwm"],
                        "dm": elm.attrib["dm"],
                        "pwp": elm.attrib["pwp"],
                        "diameter_mm": float(elm.attrib["diameter"])
                        if elm.attrib["diameter_unit"] == "mm"
                        else f"{elm.attrib['diameter']}_{elm.attrib['diameter_unit']}",
                        "source_id": elm.attrib["id"],
                        "source": "SIMONE",
                    }
                elif elm.attrib["type"] == "control valve":
                    data_valve[elm.attrib["id"]] = {
                        "from_junction": elm[0].attrib["id"],
                        "to_junction": elm[1].attrib["id"],
                        "source_name": elm.attrib["name"],
                        "type": elm.attrib["alias"]
                        if len(elm.attrib["alias"]) > 0
                        else float("nan"),
                        "pwm": elm.attrib["pwm"],
                        "dm": elm.attrib["dm"],
                        "pwp": elm.attrib["pwp"],
                        "POMax": elm.attrib["POMax"],
                        "Rin": elm.attrib["Rin"],
                        "PIMin": elm.attrib["PIMin"],
                        "Rout": elm.attrib["Rout"],
                        "diameter_mm": float(elm.attrib["diameter"])
                        if elm.attrib["diameter_unit"] == "mm"
                        else f"{elm.attrib['diameter']}_{elm.attrib['diameter_unit']}",
                        "source_id": elm.attrib["id"],
                        "source": "SIMONE",
                    }
                # create joint elements  # !!! todo
    # prepare data
    data_nodes = pd.DataFrame(data_nodes).T
    data_pipes = pd.DataFrame(data_pipes).T
    data_compressor = pd.DataFrame(data_compressor).T
    data_valve = pd.DataFrame(data_valve).T
    data = {
        "node": gpd.GeoDataFrame(data_nodes, geometry=data_nodes["geometry"], crs=crs),
        "pipe": gpd.GeoDataFrame(data_pipes, geometry=data_pipes.geometry, crs=crs),
        "compressor station": data_compressor,
        "valve": data_valve,
        # 'joint': data_elements[data_elements.type == 'joint'],
    }
    # projecting geodata to epsg 4326 if neccessary
    if crs != "epsg:4326":
        data["node"] = data["node"].to_crs(crs="epsg:4326")
        data["pipe"] = data["pipe"].to_crs(crs="epsg:4326")

    return data


def read_json(path, name):
    # read scenario and result data
    n_df = pd.read_json(f"{path}\\{name}_nodes.json", orient="records", lines=True)
    e_df = pd.read_json(f"{path}\\{name}_elements.json", orient="records", lines=True)
    return n_df, e_df
