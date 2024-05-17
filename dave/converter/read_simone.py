# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from xml.etree.ElementTree import parse

from geopandas import GeoDataFrame
from pandas import DataFrame, read_json, Series
from shapely.geometry import LineString, Point

from dave.client.dave_request import from_database
from dave.dave_structure import create_empty_dataset
from dave.settings import dave_settings


def read_simone_file(topology_path, scenario_path=None, result_path=None, crs="epsg:4326"):
    """
    This function reads given simone files in xml format

    INPUT:
        **topology_path** (str) - path to the simone network XML file \n

    OPTIONAL:
        **scenario_path** (str, default None) - path to the simone scenario file \n
        **result_path** (str, default None) -  path to the simone result file \n
        **crs** (str, default "epsg:4326") - coordinate system of the data \n

    OUTPUT:
        **data** (dict) - dict which contains all data as GeoDataFrames \n
    """
    # read data from xml
    data_nodes = {}
    data_pipes = {}
    data_compressor = {}
    data_valve = {}
    root = parse(f"{topology_path}").getroot()
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
    data_nodes = DataFrame(data_nodes).T
    data_pipes = DataFrame(data_pipes).T
    data_compressor = DataFrame(data_compressor).T
    data_valve = DataFrame(data_valve).T
    data = {
        "node": GeoDataFrame(data_nodes, geometry=data_nodes["geometry"], crs=crs),
        "pipe": GeoDataFrame(data_pipes, geometry=data_pipes.geometry, crs=crs),
        "compressor station": data_compressor,
        "valve": data_valve,
        # 'joint': data_elements[data_elements.type == 'joint'],
    }
    # projecting geodata to epsg 4326 if neccessary
    if crs != "epsg:4326":
        data["node"] = data["node"].to_crs(crs="epsg:4326")
        data["pipe"] = data["pipe"].to_crs(crs="epsg:4326")

    # read scenario data from file
    if scenario_path:
        data["node_parameter"], data["element_parameter"] = read_json(scenario_path)

    # read result data from file
    if result_path:
        data["node_results"], data["element_results"] = read_json(result_path)
    return data


def read_simone_db(network, scenario=None):
    """
    This function reads simone data from dave database

    INPUT:
        **network** (str) - simone network name \n

    OPTIONAL:
        **scenario** (str, default None) - simone scenario name \n
        **crs** (str, default "epsg:4326") - coordinate system of the data \n

    OUTPUT:
        **data** (dict) - dict which contains all data as GeoDataFrames \n
    """
    # request topology from database for given network
    data = {}
    data["node"] = from_database(database="tub", collection=f"{network}_net_node")
    data["pipe"] = from_database(database="tub", collection=f"{network}_net_pipe")
    data["valve"] = from_database(database="tub", collection=f"{network}_net_valve")
    data["compressor station"] = from_database(
        database="tub", collection=f"{network}_net_compressor station"
    )
    if scenario:
        # add parameter and result data
        data["node_parameter"] = from_database(
            database="tub", collection=f"{network}_{scenario}_parameters_nodes"
        )
        data["element_parameter"] = from_database(
            database="tub", collection=f"{network}_{scenario}_parameters_elements"
        )
        data["node_results"] = from_database(
            database="tub", collection=f"{network}_{scenario}_results_nodes"
        )
        data["element_results"] = from_database(
            database="tub", collection=f"{network}_{scenario}_results_elements"
        )

    return data


def read_json(filepath):
    # read scenario and result data
    n_df = read_json(f"{filepath}_nodes.json", orient="records", lines=True)
    e_df = read_json(f"{filepath}_elements.json", orient="records", lines=True)
    return n_df, e_df


def simone_to_dave(data_simone):
    """
    This functions converts data from simone into DAVE Format

    INPUT:
        **data_simone** (dict) - all available simone data. Including Topology \
            and optional includes scenario and result data \n

    """
    # create empty dave dataset
    grid_data = create_empty_dataset()
    # write data into dave dataset
    grid_data.hp_data.hp_junctions = data_simone["node"]
    grid_data.hp_data.hp_pipes = data_simone["pipe"]
    grid_data.hp_data.hp_pipes["max_pressure_bar"] = 80
    grid_data.components_gas.compressors = data_simone["compressor station"]
    grid_data.components_gas.valves = data_simone["valve"]

    # add dave name
    grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.reset_index(drop=True)
    grid_data.hp_data.hp_junctions.insert(
        0,
        "dave_name",
        Series(list(map(lambda x: f"junction_1_{x}", grid_data.hp_data.hp_junctions.index))),
    )
    grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.reset_index(drop=True)
    grid_data.hp_data.hp_pipes.insert(
        0,
        "dave_name",
        Series(list(map(lambda x: f"pipe_1_{x}", grid_data.hp_data.hp_pipes.index))),
    )
    # TODO: ids ins dave namen ändern
    # auch noch dave name für valve und cs

    # write scenario data into dave dataset
    if "node_parameter" in data_simone.keys() and "element_parameter" in data_simone.keys():
        # filter scenario data
        n_par = data_simone["node_parameter"]
        e_par = data_simone["element_parameter"]
        # create sources
        factor_mw_to_kb_per_s = dave_settings()["factor_mw_to_kb_per_s"]
        grid_data.components_gas.sources = n_par[
            (n_par["supply"] == 1)
            & (n_par["parameters"].apply(lambda x: "Q" in x and "PSET" not in x))
        ]
        grid_data.components_gas.sources["mdot_kg_per_s"] = grid_data.components_gas.sources[
            "values"
        ].apply(lambda x: x[0] * factor_mw_to_kb_per_s)
        grid_data.components_gas.sources.rename(columns={"name": "source_name"}, inplace=True)
        grid_data.components_gas.sources["junction"] = grid_data.components_gas.sources[
            "source_name"
        ].apply(
            lambda x: grid_data.hp_data.hp_junctions[
                grid_data.hp_data.hp_junctions.source_name == x
            ]
            .iloc[0]
            .source_id
        )

        # create sinks
        grid_data.components_gas.sinks = n_par[
            (n_par["supply"] == 0) & (n_par["parameters"].apply(lambda x: "Q" in x))
        ]
        grid_data.components_gas.sinks["mdot_kg_per_s"] = grid_data.components_gas.sinks[
            "values"
        ].apply(lambda x: x[0] * factor_mw_to_kb_per_s)
        grid_data.components_gas.sinks.rename(columns={"name": "source_name"}, inplace=True)
        grid_data.components_gas.sinks["junction"] = grid_data.components_gas.sinks[
            "source_name"
        ].apply(
            lambda x: grid_data.hp_data.hp_junctions[
                grid_data.hp_data.hp_junctions.source_name == x
            ]
            .iloc[0]
            .source_id
        )

        # adjust valve data
        grid_data.components_gas.valves[
            "opened"
        ] = grid_data.components_gas.valves.source_name.apply(
            lambda x: True
            if e_par[e_par["name"] == x].iloc[0]["values"][0] in ["BP", "ON"]
            else False
        )

        # adjust compressor stations
        # TODO: add compressor station adjustments based on e_par

        # adjust junction data for external grid junctions
        ext_grid = n_par[
            (n_par["supply"] == 1) & (n_par["parameters"].apply(lambda x: "PSET" in x))
        ]
        for _, junc in ext_grid.iterrows():
            junction_idx = grid_data.hp_data.hp_junctions[
                grid_data.hp_data.hp_junctions.source_name == junc["name"]
            ].index[0]
            grid_data.hp_data.hp_junctions.at[
                junction_idx, f"Pset_{ext_grid.units.iloc[0][1]}"
            ] = junc["values"][1]

    # write result data into dave dataset
    if "node_results" in data_simone.keys() and "element_results" in data_simone.keys():
        # filter scenario data
        n_res = data_simone["node_results"]
        e_res = data_simone["element_results"]

        # add junction result data
        grid_data.hp_data.hp_junctions[
            "res_simone_p_barg"
        ] = grid_data.hp_data.hp_junctions.source_name.apply(
            lambda x: n_res[n_res["name"] == x].iloc[0]["values"][1]
            if not n_res[n_res["name"] == x].empty
            else "nan"
        )
        grid_data.hp_data.hp_junctions[
            "res_simone_q_eff_mw"
        ] = grid_data.hp_data.hp_junctions.source_name.apply(
            lambda x: n_res[n_res["name"] == x].iloc[0]["values"][0]
            if not n_res[n_res["name"] == x].empty
            else "nan"
        )
        # add pipe result data
        pipe_res = e_res[e_res.type == "pipe"]
        grid_data.hp_data.hp_pipes[
            "res_simone_p_barg"
        ] = grid_data.hp_data.hp_pipes.source_name.apply(
            lambda x: pipe_res[pipe_res["name"] == x].iloc[0]["values"][2]
        )
        grid_data.hp_data.hp_pipes[
            "res_simone_v_m/s"
        ] = grid_data.hp_data.hp_pipes.source_name.apply(
            lambda x: pipe_res[pipe_res["name"] == x].iloc[0]["values"][1]
        )

    return grid_data
