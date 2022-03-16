# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import networkx as nx
import pandas as pd
from tqdm import tqdm

from dave.settings import dave_settings


def disconnected_nodes(nodes, edges, min_number_nodes):
    """
    converts nodes and lines to a networkX graph

    INPUT:
        **nodes** (DataFrame) - Dataset of nodes with DaVe name  \n
        **edges** (DataFrame) - Dataset of edges (lines, pipelines) with DaVe name \n
    OUTPUT:
        **nodes** (set) - all dave names for nodes which are not connected to a grid with a minumum
                          number of nodes \n
    """
    # create empty graph
    graph = nx.Graph()
    # create nodes
    graph.add_nodes_from(nodes.dave_name.to_list())
    # create edges
    graph.add_edges_from(edges.apply(lambda x: (x["from_node"], x["to_node"]), axis=1).to_list())
    # check for disconnected nodes
    disconnected_nodes = set()
    connected_elements = list(nx.connected_components(graph))
    for elements in connected_elements:
        if len(elements) < min_number_nodes:
            for node in elements:
                disconnected_nodes.add(node)
    return disconnected_nodes


def clean_disconnected_elements_power(grid_data, min_number_nodes):
    """
    This function clean up disconnected elements for the diffrent power grid levels
    """
    # get disconnected nodes
    nodes_all = pd.concat(
        [
            grid_data.ehv_data.ehv_nodes,
            grid_data.hv_data.hv_nodes,
            grid_data.mv_data.mv_nodes,
            grid_data.lv_data.lv_nodes,
        ],
        ignore_index=True,
    )
    lines_all = pd.concat(
        [
            grid_data.ehv_data.ehv_lines,
            grid_data.hv_data.hv_lines,
            grid_data.mv_data.mv_lines,
            grid_data.lv_data.lv_lines,
        ],
        ignore_index=True,
    )
    lines_all.rename(columns={"from_bus": "from_node", "to_bus": "to_node"}, inplace=True)
    trafos_all = pd.concat(
        [
            grid_data.components_power.transformers.ehv_ehv,
            grid_data.components_power.transformers.ehv_hv,
            grid_data.components_power.transformers.hv_mv,
            grid_data.components_power.transformers.mv_lv,
        ],
        ignore_index=True,
    )
    trafos_all.rename(columns={"bus_hv": "from_node", "bus_lv": "to_node"}, inplace=True)
    nodes_dis = list(
        disconnected_nodes(
            nodes=nodes_all,
            edges=pd.concat(
                [lines_all, trafos_all],
                ignore_index=True,
            ),
            min_number_nodes=min_number_nodes,
        )
    )
    # drop elements for each level which are disconnected
    for level in grid_data.target_input.power_levels.iloc[0]:
        nodes = grid_data[f"{level}_data"][f"{level}_nodes"]
        lines = grid_data[f"{level}_data"][f"{level}_lines"]
        # filter disconnected lines based on disconnected nodes
        lines_dis = lines[lines.from_bus.isin(nodes_dis)]
        # filter power components which connected to disconnected junctions
        power_components = list(grid_data.components_power.keys())
        for component_typ in power_components:
            if (
                component_typ not in ["transformers", "substations"]
                and not grid_data.components_power[f"{component_typ}"].empty
            ):
                components = grid_data.components_power[f"{component_typ}"]
                # delet needless power components
                grid_data.components_power[f"{component_typ}"].drop(
                    components[components.bus.isin(nodes_dis)].index.to_list(), inplace=True
                )
            elif component_typ == "transformers":
                # this components have a sub type
                power_components_sub = list(grid_data.components_power[f"{component_typ}"].keys())
                for component_subtyp in power_components_sub:
                    if not grid_data.components_power[f"{component_typ}"][
                        f"{component_subtyp}"
                    ].empty:
                        components = grid_data.components_power[f"{component_typ}"][
                            f"{component_subtyp}"
                        ]
                        # delet needless power components
                        grid_data.components_power[f"{component_typ}"][f"{component_subtyp}"].drop(
                            components[
                                components.bus_hv.isin(nodes_dis)
                                & components.bus_lv.isin(nodes_dis)
                            ].index.to_list(),
                            inplace=True,
                        )
            elif component_typ == "substation":
                # this components have a sub type
                power_components_sub = list(grid_data.components_power[f"{component_typ}"].keys())
                for component_subtyp in power_components_sub:
                    if not grid_data.components_power[f"{component_typ}"][
                        f"{component_subtyp}"
                    ].empty:
                        components = grid_data.components_power[f"{component_typ}"][
                            f"{component_subtyp}"
                        ]
                        # delet needless power components
                        substation_dis = nodes[nodes.dave_name.isin(nodes_dis)].subst_dave_name
                        if ~pd.isnull(substation_dis).all():
                            grid_data.components_power[f"{component_typ}"][
                                f"{component_subtyp}"
                            ].drop(
                                components[components.dave_name.isin(nodes_dis)].index.to_list(),
                                inplace=True,
                            )

        # delet needless nodes and lines
        grid_data[f"{level}_data"][f"{level}_nodes"].drop(
            nodes[nodes.dave_name.isin(nodes_dis)].index.to_list(), inplace=True
        )
        grid_data[f"{level}_data"][f"{level}_lines"].drop(lines_dis.index.to_list(), inplace=True)


def clean_disconnected_elements_gas(grid_data, min_number_nodes):
    """
    This function clean up disconnected elements for the diffrent gas grid levels
    """
    # get disconnected junctions
    junctions_all = pd.concat(
        [
            grid_data.hp_data.hp_junctions,
            grid_data.mp_data.mp_junctions,
            grid_data.lp_data.lp_junctions,
        ],
        ignore_index=True,
    )
    pipelines_all = pd.concat(
        [grid_data.hp_data.hp_pipes, grid_data.mp_data.mp_pipes, grid_data.lp_data.lp_pipes],
        ignore_index=True,
    )  # !!! Todo: Verbindung der Netzebenen mit einbeziehen
    pipelines_all.rename(
        columns={"from_junction": "from_node", "to_junction": "to_node"}, inplace=True
    )
    junctions_dis = list(
        disconnected_nodes(
            nodes=junctions_all,
            edges=pipelines_all,
            min_number_nodes=min_number_nodes,
        )
    )
    # drop elements for each level which are disconnected
    for level in grid_data.target_input.gas_levels.iloc[0]:
        junctions = grid_data[f"{level}_data"][f"{level}_junctions"]
        pipelines = grid_data[f"{level}_data"][f"{level}_pipes"]
        # filter disconnected pipelines based on disconnected junctions
        pipelines_dis = pipelines[pipelines.from_junction.isin(junctions_dis)]
        # filter gas components which connected to disconnected junctions
        gas_components = list(grid_data.components_gas.keys())
        for component_typ in gas_components:
            if not grid_data.components_gas[f"{component_typ}"].empty:
                components = grid_data.components_gas[f"{component_typ}"]
                # delet needless gas components
                grid_data.components_gas[f"{component_typ}"].drop(
                    components[components.junction.isin(junctions_dis)].index.to_list(),
                    inplace=True,
                )
        # delet needless junctions and pipelines
        grid_data[f"{level}_data"][f"{level}_junctions"].drop(
            junctions[junctions.dave_name.isin(junctions_dis)].index.to_list(), inplace=True
        )
        grid_data[f"{level}_data"][f"{level}_pipes"].drop(
            pipelines_dis.index.to_list(), inplace=True
        )


def clean_wrong_piplines(grid_data):
    """
    This function drops gas pipelines which have wrong charakteristics
    """
    for level in grid_data.target_input.gas_levels.iloc[0]:
        pipelines = grid_data[f"{level}_data"][f"{level}_pipes"]
        # check if piplines have the same start and end point
        pipelines_equal = pipelines[pipelines.from_junction == pipelines.to_junction]
        # delet needless pipelines
        grid_data[f"{level}_data"][f"{level}_pipes"].drop(
            pipelines_equal.index.to_list(), inplace=True
        )


def clean_wrong_lines(grid_data):
    """
    This function drops power lines which have wrong charakteristics
    """
    for level in grid_data.target_input.power_levels.iloc[0]:
        pipelines = grid_data[f"{level}_data"][f"{level}_lines"]
        # check if piplines have the same start and end point
        lines_equal = pipelines[pipelines.from_bus == pipelines.to_bus]
        # delet needless pipelines
        grid_data[f"{level}_data"][f"{level}_lines"].drop(lines_equal.index.to_list(), inplace=True)


# Funktion um Leitungen zu finden die Anfangs und Endknoten gleich haben rausfiltern


def clean_up_data(grid_data, min_number_nodes=dave_settings()["min_number_nodes"]):
    """
    This function clean up the DaVe Dataset for diffrent kinds of failures
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="clean up dave dataset:             ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # --- clean up power grid data
    if grid_data.target_input.iloc[0].power_levels:
        # clean up disconnected elements
        clean_disconnected_elements_power(grid_data, min_number_nodes)
        # update progress
        pbar.update(40)
        # clean up lines with wrong characteristics
        clean_wrong_lines(grid_data)
        # update progress
        pbar.update(10)
    else:
        # update progress
        pbar.update(50)
    # --- clean up gas grid data
    if grid_data.target_input.iloc[0].gas_levels:
        # clean up disconnected elements
        clean_disconnected_elements_gas(grid_data, min_number_nodes)
        # update progress
        pbar.update(40)
        # clean up pipelines with wrong characteristics
        clean_wrong_piplines(grid_data)
        # update progress
        pbar.update(10)
    else:
        # update progress
        pbar.update(50)
    # close progress bar
    pbar.close()


# !!! Todo's clean up:
# Leitungen mit Länge 0
# pandapower diagnostic nochmal genauer anschauen
