import os
import pandas as pd
import geopandas as gpd

# imports from dave
from dave.dave_structure import davestructure
from dave import __version__
from dave import dave_output_dir
from dave.topology import target_area, create_ehv_topology, create_hv_topology, create_mv_topology, create_lv_topology
from dave.plotting import plot_target_area, plot_grid_data, plot_landuse
from dave.components import power_components
from dave.model import create_power_grid



def create_empty_dataset():
    """
    This function initializes the dave datastructure.

    OUTPUT:
        **grid_data** (attrdict) - dave attrdict with empty tables:

    EXAMPLE:
        grid_data = create_empty_dataset()

    """
    # define crs
    crs = 'EPSG:4326'
    # define dave structure
    grid_data = davestructure({
                 # target data
                 'area': gpd.GeoDataFrame([], crs=crs),
                 'target_input': pd.DataFrame(),
                 'buildings': davestructure({'building_centroids': gpd.GeoSeries([], crs=crs),
                                             'commercial': gpd.GeoDataFrame([], crs=crs),
                                             'for_living': gpd.GeoDataFrame([], crs=crs),
                                             'other': gpd.GeoDataFrame([], crs=crs)
                                             }),
                 'roads': davestructure({'roads': gpd.GeoDataFrame([], crs=crs),
                                         'roads_plot': gpd.GeoDataFrame([], crs=crs),
                                         'road_junctions': gpd.GeoSeries([], crs=crs)
                                         }),
                 'landuse': gpd.GeoDataFrame([], crs=crs),
                 # power grid data
                 'ehv_data': davestructure({'ehv_substations': gpd.GeoDataFrame([], crs=crs),
                                            'ehv_nodes': gpd.GeoDataFrame([], crs=crs),
                                            'ehv_lines': gpd.GeoDataFrame([], crs=crs)
                                            }),
                 'hv_data': davestructure({'hv_nodes': gpd.GeoDataFrame([], crs=crs),
                                           'hv_lines': gpd.GeoDataFrame([], crs=crs)
                                            }),
                 'mv_data': davestructure({'mv_nodes': gpd.GeoDataFrame([], crs=crs),
                                           'mv_lines': gpd.GeoDataFrame([], crs=crs)
                                            }),
                 'lv_data': davestructure({'lv_nodes': gpd.GeoDataFrame([], crs=crs),
                                           'lv_lines': gpd.GeoDataFrame([], crs=crs)
                                           }),
                 'components_power':davestructure({'loads':gpd.GeoDataFrame([], crs=crs),
                                                   'renewable_powerplants':gpd.GeoDataFrame([], crs=crs),
                                                   'conventional_powerplants': gpd.GeoDataFrame([], crs=crs),
                                                   'transformers':davestructure({'ehv_ehv': gpd.GeoDataFrame([], crs=crs),
                                                                                 'ehv_hv': gpd.GeoDataFrame([], crs=crs),
                                                                                 'hv_mv': gpd.GeoDataFrame([], crs=crs),
                                                                                 'mv_lv': gpd.GeoDataFrame([], crs=crs)
                                                                                 })
                                                   }),
                 # auxillary
                 'dave_version': __version__
                 })
    return grid_data

def create_grid(postalcode=None, town_name=None, federal_state=None,
                own_area=None, power_levels=['ALL'], gas_levels=['ALL'],
                plot=True, convert = True):
    """
    This is the main function of dave. This function generates automaticly grid
    models for power and gas networks in the defined target area
    INPUT:
        
        One of these parameters must be set:
        **postalcode** (List of strings) - numbers of the target postalcode areas. 
                                           it could also be choose ['ALL'] for all postalcode areas in germany
        **town_name** (List of strings) - names of the target towns
                                          it could also be choose ['ALL'] for all citys in germany
        **federal_state** (List of strings) - names of the target federal states
                                              it could also be choose ['ALL'] for all federal states in germany
        **own_area** (string) - full path to a shape file which includes own target area (e.g. "C:/Users/name/test/test.shp")
        
    OPTIONAL:
        **power_levels** (list, default ['ALL']) - this parameter defines which power levels should be considered
                                                   options: 'EHV','HV','MV','LV'. There could be choose: one level, more 
                                                   than one level or 'ALL' for all levels
        **gas_levels** (list, default ['ALL']) - this parameter defines which gas levels should be considered
                                                 options: 'HP','MP','LP'. There could be choose: one level, more 
                                                 than one level or 'ALL' for all levels
        **plot** (boolean, default True) - if this value is true dave creates plottings automaticly
        *convert** (boolean, default True) _ if this value is true dave will be convert the grid automaticly to pandapower and pandapipes
        
    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure
        **net_power**
        **net_pipes**
    
    EXAMPLE:

    """
    
    
    """
    Hier eine funktion schreiben die alle modellierungsfunktionen so aufruft das aus einem Ortsnamen 
    oder einer PLZ ein fertiges Netz für strom und gas rauskommt

    hier berücksichtigen das verschiedene Spannungsebenen, verschiedene funktionen benötigen
    Parameter voltage_level ist list of string mit allen SPannungsebeen die gewünsct sind ['HS','MS','NS']
    

    
    Evt. noch power_levels gegen voltage_levels tauschen (das müsste aber in alle Skripten geprüft werden)
    Evt. noch gas_levels gegen pressure_levels tauschen (das müsste aber in alle Skripten geprüft werden)
    """
   
    
    # create empty datastructure
    grid_data = create_empty_dataset()
    
    # --- adapt level inputs
    # set level inputs to upper strings
    for i in range(0,len(power_levels)):
        power_levels[i] = power_levels[i].upper()
    for i in range(0,len(gas_levels)):
        gas_levels[i] = gas_levels[i].upper()
    # convert input value 'ALL'
    if power_levels == ['ALL']:
            power_levels = ['EHV','HV','MV','LV']
    if gas_levels == ['ALL']:
        gas_levels = ['HP','MP','LP']
    # sort level inputs
    for i in range(0, len(power_levels)):
        if power_levels[i] == 'EHV':
            power_levels[i] = 0
        if power_levels[i] == 'HV':
            power_levels[i] = 1
        if power_levels[i] == 'MV':
            power_levels[i] = 2
        if power_levels[i] == 'LV':
            power_levels[i] = 3
    power_levels.sort()
    for i in range(0, len(power_levels)):
        if power_levels[i] == 0:
            power_levels[i] = 'EHV'
        if power_levels[i] == 1:
            power_levels[i] = 'HV'
        if power_levels[i] == 2:
            power_levels[i] = 'MV'
        if power_levels[i] == 3:
            power_levels[i] = 'LV'
    for i in range(0, len(gas_levels)):
        if gas_levels[i] == 'HP':
            gas_levels[i] = 0
        if gas_levels[i] == 'MP':
            gas_levels[i] = 1
        if gas_levels[i] == 'LP':
            gas_levels[i] = 2
    gas_levels.sort()
    for i in range(0, len(gas_levels)):
        if gas_levels[i] == 0:
            gas_levels[i] = 'HP'
        if gas_levels[i] == 1:
            gas_levels[i] = 'MP'
        if gas_levels[i] == 2:
            gas_levels[i] = 'LP'

    # --- create desired power grid levels
    if power_levels ==  ['EHV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=True).target()
        create_ehv_topology(grid_data)
        power_components(grid_data)
    elif power_levels == ['HV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_hv_topology(grid_data)
    elif power_levels == ['MV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_mv_topology(grid_data)
    elif power_levels == ['LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_lv_topology(grid_data)
        #power_components(grid_data)
    elif power_levels == ['EHV', 'HV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_ehv_topology(grid_data)
        create_hv_topology(grid_data)
        #power_components(grid_data)
    elif power_levels == ['EHV', 'MV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_ehv_topology(grid_data)
        create_mv_topology(grid_data)
    elif power_levels == ['EHV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_ehv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['HV', 'MV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_hv_topology(grid_data)
        create_mv_topology(grid_data)
    elif power_levels == ['HV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_hv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['MV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_mv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['EHV', 'HV', 'MV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area, 
                    buffer=0, roads=False, roads_plot=False, 
                    buildings=False, landuse=False).target()
        create_ehv_topology(grid_data)
        create_hv_topology(grid_data)
        create_mv_topology(grid_data)
    elif power_levels == ['EHV', 'HV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_ehv_topology(grid_data)
        create_hv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['EHV', 'MV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_ehv_topology(grid_data)
        create_mv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['HV', 'MV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_hv_topology(grid_data)
        create_mv_topology(grid_data)
        create_lv_topology(grid_data)
    elif power_levels == ['EHV', 'HV', 'MV', 'LV']:
        # create topology
        target_area(grid_data, power_levels=power_levels, gas_levels=gas_levels, 
                    postalcode=postalcode, town_name=town_name,
                    federal_state=federal_state, own_area=own_area,
                    buffer=0, roads=True, roads_plot=True,
                    buildings=True, landuse=True).target()
        create_ehv_topology(grid_data)
        create_hv_topology(grid_data)
        create_mv_topology(grid_data)
        create_lv_topology(grid_data)
    else:
        print('no voltage level was choosen or their is a failure in the input value.')
        print(f'the input for the power levels was: {power_levels}')
        print('---------------------------------------------------')
    
    # --- create desired gas grid levels
    if gas_levels == ['HP']:
        pass
    elif gas_levels == ['MP']:
        pass
    elif gas_levels == ['LP']:
        pass
    elif gas_levels == ['HP', 'MP']:
        pass
    elif gas_levels == ['HP', 'LP']:
        pass
    elif gas_levels == ['MP', 'LP']:
        pass
    elif gas_levels == ['HP', 'MP', 'LP']:
        pass 
    else:
        print('no gas level was choosen or their is a failure in the input value.')
        print(f'the input for the gas levels was: {gas_levels}')
        print('-----------------------------------------------')
        
    # create dave output folder on desktop for plotting and converted models
    if plot or convert:
        print('Save plots and converted grid models at the following path:')
        print(dave_output_dir)
        print('-----------------------------------------------------------------------')
        if not os.path.exists(dave_output_dir):
            os.makedirs(dave_output_dir)
    # plot informations
    if plot:
        plot_target_area(grid_data)
        plot_grid_data(grid_data)
        plot_landuse(grid_data)
    # convert into pandapower and pandapipes
    if convert and power_levels:
        net_power = create_power_grid(grid_data)
    else:
        net_power = None
    if convert and gas_levels:
        pass # hier noch create pandapipes funktion rein
    
    # return
    if net_power: # hier noch ein elif rein für net_gas    
        return grid_data, net_power
    else:
        return grid_data
