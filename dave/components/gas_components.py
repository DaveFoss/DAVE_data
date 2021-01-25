

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


def gas_components(grid_data, compressor, source, storage_gas):
    """
    This function calls all the functions for creating the gas components in the wright order
    """
    # add compressors
    if compressor:
        compressors(grid_data)
    # add sources
    if source:
        sources(grid_data)
    # add storages
    if storage_gas:
        storages_gas(grid_data)
