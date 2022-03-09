import networkx as nx
import pandas as pd

from dave.settings import dave_settings


def disconnected_nodes(nodes, edges, grid_type, min_number_nodes):
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
    if grid_type == "gas":
        graph.add_edges_from(
            edges.apply(lambda x: (x["from_junction"], x["to_junction"]), axis=1).to_list()
        )
    elif grid_type == "power":
        graph.add_edges_from(edges.apply(lambda x: (x["from_bus"], x["to_bus"]), axis=1).to_list())
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
    nodes_dis = list(
        disconnected_nodes(
            nodes=nodes_all, edges=lines_all, grid_type="power", min_number_nodes=min_number_nodes
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
            elif (
                component_typ == "transformers"
                and not grid_data.components_power[f"{component_typ}"].empty
            ):
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
                                | components.bus_lv.isin(nodes_dis)
                            ].index.to_list(),
                            inplace=True,
                        )
                # !!! Todo: Hier muss noch gecheckt werden ob beide Knoten nicht genutzt werden.
            elif (
                component_typ == "substation"
                and not grid_data.components_power[f"{component_typ}"].empty
            ):
                pass
                # !!! Substations müssen noch gemacht werden

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
    )
    junctions_dis = list(
        disconnected_nodes(
            nodes=junctions_all,
            edges=pipelines_all,
            grid_type="gas",
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


# Funktion um Leitungen zu finden die Anfangs und Endknoten gleich haben rausfiltern


def clean_up_data(grid_data, min_number_nodes=dave_settings()["min_number_nodes"]):
    """
    This function clean up the DaVe Dataset for diffrent kinds of failures
    """
    # clean up disconnected elements
    if grid_data.target_input.iloc[0].power_levels:
        clean_disconnected_elements_power(grid_data, min_number_nodes)
    if grid_data.target_input.iloc[0].gas_levels:
        clean_disconnected_elements_gas(grid_data, min_number_nodes)
    # clean up


# !!! Todo's clean up:
# Leitungen mit Länge 0
# Leitungen mit selben Anfangs und Endpunkt
# power und gas components die mit disconnected nodes verbunden sind
# pandapower diagnostic nochmal genauer anschauen
