

def sources(grid_data):
    """
    This function collects the data for production
    """
    pass


def compressors(grid_data):
    pass


def storages_gas(grid_data):
    pass
    # gas storages in germany
    # read_gas_storage_ugs()


def gas_components(grid_data, compressors, sources, storages_gas):
    """
    This function calls all the functions for creating the gas components in the wright order
    """
    # add compressors
    compressors(grid_data)
    # add sources
    sources(grid_data)
    # add storages
    storages_gas(grid_data)
