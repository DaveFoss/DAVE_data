def sources(grid_data):
    """
    This function collects the data for gas production
    """
    # read_scigridgas_iggielgn()
    pass


def compressors(grid_data):
    # read_scigridgas_iggielgn()
    pass


def storages_gas(grid_data):
    pass
    # gas storages in germany
    # read_gas_storage_ugs()
    # read_scigridgas_iggielgn()


def valve(grid_data):
    """
    This function collects the data for valves between junctions
    """
    # At this time there are no data source for valves availible
    pass


def sink(grid_data):
    """
    This function collects the data for gas consumers
    """
    # read_scigridgas_iggielgn() consumers
    pass


def gas_components(grid_data, compressor, source, storage_gas, valve):
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
    # add valves
    if valve:
        valve(grid_data)
