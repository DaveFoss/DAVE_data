import pandapipes as ppi


def create_gas_grid(grid_data):
    """
    This function creates a pandapipes network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:
        **net** (attrdict) - pandapipes attrdict with grid data
    """
    print('create pandapipes network')
    print('----------------------------------')
    # create empty network
    net = ppi.create_empty_network()
    # add dave version
    net['dave_version'] = grid_data.dave_version

    # --- create high pressure topology
    # create junctions
