from dave.datapool import read_scigridgas_iggielgn


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


def valves(grid_data):
    """
    This function collects the data for valves between junctions
    """
    # At this time there are no data source for valves availible
    pass


def sinks(grid_data):
    """
    This function collects the data for gas consumers
    """
    # read_scigridgas_iggielgn() consumers
    pass


def gas_components(grid_data, compressor, sinks, sources, storages_gas, valves):
    """
    This function calls all the functions for creating the gas components in the wright order
    """
    # read high pressure grid data from dave datapool (scigridgas igginl)
    if any([compressor, sources, sinks, storages_gas]):
        scigrid_data, meta_data = read_scigridgas_iggielgn()
    # add compressors
    if compressor:
        compressors(grid_data)
    # add sinks
    if sinks:
        sinks(grid_data)
    # add sources
    if sources:
        sources(grid_data)
    # add storages
    if storages_gas:
        storages_gas(grid_data)
    # add valves
    if valves:
        valves(grid_data)
