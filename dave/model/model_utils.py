import networkx as nx

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
    graph.add_edges_from(
        edges.apply(lambda x: (x["from_junction"], x["to_junction"]), axis=1).to_list()
    )
    # check for disconnected nodes
    disconnected_nodes = set()
    connected_elements = list(nx.connected_components(graph))
    for elements in connected_elements:
        if len(elements) < min_number_nodes:
            for node in elements:
                disconnected_nodes.add(node)
    return disconnected_nodes


# Funktion um Leitungen zu finden die Anfangs und Endknoten gleich haben rausfiltern


def clean_up_data(grid_data, min_number_nodes=dave_settings()["min_number_nodes"]):
    """
    This function clean up needless nodes and lines for the diffrent grid levels
    """
    # --- clean up power grid data

    # --- clean up gas grid data
    # get disconnected junctions
    for level in grid_data.target_input.gas_levels.iloc[0]:
        junctions = grid_data[f"{level}_data"][f"{level}_junctions"]
        pipelines = grid_data[f"{level}_data"][f"{level}_pipes"]
        junctions_dis = list(
            disconnected_nodes(nodes=junctions, edges=pipelines, min_number_nodes=min_number_nodes)
        )
        # filter disconnected pipelines based on disconnected junctions
        pipelines_dis = pipelines[
            (pipelines.from_junction.isin(junctions_dis))
            | (pipelines.to_junction.isin(junctions_dis))
        ]

        # filter components which connected to disconnected junctions

        # delet needless elements
        grid_data[f"{level}_data"][f"{level}_junctions"].drop(
            junctions[junctions.dave_name.isin(junctions_dis)].index.to_list(), inplace=True
        )
        grid_data[f"{level}_data"][f"{level}_pipes"].drop(
            pipelines_dis.index.to_list(), inplace=True
        )
