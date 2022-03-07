import matplotlib.pyplot as plt
import networkx as nx


def create_nx_graph(nodes, edges):
    """
    converts nodes and lines to a networkX graph

    INPUT:
        **nodes** (DataFrame) - Dataset of nodes with DaVe name  \n
        **edges** (DataFrame) - Dataset of edges (lines, pipelines) with DaVe name \n
    """
    # create empty graph
    G = nx.Graph()
    # create nodes
    G.add_nodes_from(nodes.dave_name.to_list())
    # create edges
    G.add_edges_from(
        edges.apply(lambda x: (x["from_junction"], x["to_junction"]), axis=1).to_list()
    )
    nx.draw(G, node_size=10)
    plt.show()
