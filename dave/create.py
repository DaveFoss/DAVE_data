import os
import pandas as pd
import geopandas as gpd
import shutil

# imports from dave
from dave.dave_structure import davestructure
from dave import __version__
from dave import dave_output_dir, dave_dir
from dave.io_dave import write_dataset
from dave.topology import *
from dave.plotting import *
from dave.components import *
from dave.model import *
from dave.datapool import *
from dave.toolbox import create_interim_area


def create_empty_dataset():
    """
    This function initializes the dave datastructure.

    OUTPUT:
        **grid_data** (attrdict) - dave attrdict with empty tables

    EXAMPLE:
        grid_data = create_empty_dataset()

    """
    # define dave structure
    grid_data = davestructure({
                 # target data
                 'area': gpd.GeoDataFrame([]),
                 'target_input': pd.DataFrame(),
                 'buildings': davestructure({'commercial': gpd.GeoDataFrame([]),
                                             'for_living': gpd.GeoDataFrame([]),
                                             'other': gpd.GeoDataFrame([])
                                             }),
                 'roads': davestructure({'roads': gpd.GeoDataFrame([]),
                                         'roads_plot': gpd.GeoDataFrame([]),
                                         'road_junctions': gpd.GeoSeries([])
                                         }),
                 'landuse': gpd.GeoDataFrame([]),
                 # power grid data
                 'ehv_data': davestructure({'ehv_substations': gpd.GeoDataFrame([]),
                                            'ehv_nodes': gpd.GeoDataFrame([]),
                                            'ehv_lines': gpd.GeoDataFrame([])
                                            }),
                 'hv_data': davestructure({'hv_nodes': gpd.GeoDataFrame([]),
                                           'hv_lines': gpd.GeoDataFrame([])
                                           }),
                 'mv_data': davestructure({'mv_nodes': gpd.GeoDataFrame([]),
                                           'mv_lines': gpd.GeoDataFrame([])
                                           }),
                 'lv_data': davestructure({'lv_nodes': gpd.GeoDataFrame([]),
                                           'lv_lines': gpd.GeoDataFrame([])
                                           }),
                 'components_power': davestructure({'loads': gpd.GeoDataFrame([]),
                                                    'renewable_powerplants': gpd.GeoDataFrame([]),
                                                    'conventional_powerplants': gpd.GeoDataFrame([]),
                                                    'transformers': davestructure({'ehv_ehv': gpd.GeoDataFrame([]),
                                                                                   'ehv_hv': gpd.GeoDataFrame([]),
                                                                                   'hv_mv': gpd.GeoDataFrame([]),
                                                                                   'mv_lv': gpd.GeoDataFrame([])
                                                                                   })
                                                    }),
                 # gas grid data
                 'hp_data': davestructure({'hp_junctions': gpd.GeoDataFrame([]),
                                           'hp_pipes': gpd.GeoDataFrame([])
                                           }),
                 'mp_data': davestructure({'mp_junctions': gpd.GeoDataFrame([]),
                                           'mp_pipes': gpd.GeoDataFrame([])
                                           }),
                 'lp_data': davestructure({'lp_junctions': gpd.GeoDataFrame([]),
                                           'lp_pipes': gpd.GeoDataFrame([])
                                           }),
                 'components_gas': davestructure({'sinks': gpd.GeoDataFrame([]),
                                                  'sources': gpd.GeoDataFrame([]),
                                                  }),
                 # auxillary
                 'dave_version': __version__,
                 'meta_data': {}
                 })
    return grid_data


def create_grid(postalcode=None, town_name=None, federal_state=None,
                own_area=None, power_levels=[], gas_levels=[],
                plot=True, convert=True, opt_model=True, combine_areas=[]):
    """
    This is the main function of dave. This function generates automaticly grid
    models for power and gas networks in the defined target area
    INPUT:

        One of these parameters must be set:
        **postalcode** (List of strings) - numbers of the target postalcode areas.
                                           it could also be choose ['ALL'] for all postalcode areas
                                           in germany
        **town_name** (List of strings) - names of the target towns
                                          it could also be choose ['ALL'] for all citys in germany
        **federal_state** (List of strings) - names of the target federal states
                                              it could also be choose ['ALL'] for all federal states
                                              in germany
        **own_area** (string) - full path to a shape file which includes own target area
                                (e.g. "C:/Users/name/test/test.shp")

    OPTIONAL:
        **power_levels** (list, default []) - this parameter defines which power levels should be considered
                                              options: 'EHV','HV','MV','LV', [].
                                              there could be choose: one level, multiple levels or 'ALL'
        **gas_levels** (list, default []) - this parameter defines which gas levels should be considered
                                            options: 'HP','MP','LP', [].
                                            there could be choose: one level, multiple levels or 'ALL'
        **plot** (boolean, default True) - if this value is true dave creates plottings automaticly
        **convert** (boolean, default True) - if this value is true dave will be convert the grid
                                              automaticly to pandapower and pandapipes
        **opt_model** (boolean, default True) - if this value is true dave will be use the optimal
                                                power flow calculation to get no boundary violations
        **combine_areas** (list, default []) - this parameter defines on which power levels not
                                               connected areas should combined
                                               options: 'EHV','HV','MV','LV', []

    OUTPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure
        **net_power**
        **net_pipes**

    EXAMPLE:
        from dave.create import create_grid

        grid_data  = create_grid(town_name=['Kassel', 'Baunatal']
                                 power_levels=['HV', 'MV'],
                                 gas_levels=['HP'],
                                 plot=False,
                                 convert = False)

    """
    # create empty datastructure
    grid_data = create_empty_dataset()

    # --- adapt level inputs
    # set level inputs to upper strings
    power_levels = list(map(str.upper, power_levels))
    gas_levels = list(map(str.upper, gas_levels))
    combine_areas = list(map(str.upper, combine_areas))
    # convert input value 'ALL'
    if power_levels == ['ALL']:
        power_levels = ['EHV', 'HV', 'MV', 'LV']
    if gas_levels == ['ALL']:
        gas_levels = ['HP', 'MP', 'LP']
    # sort level inputs
    order_power = ['EHV', 'HV', 'MV', 'LV']
    power_sort = sorted(list(map(lambda x: order_power.index(x), power_levels)))
    power_levels = list(map(lambda x: order_power[x], power_sort))
    order_gas = ['HP', 'MP', 'LP']
    gas_sort = sorted(list(map(lambda x: order_gas.index(x), gas_levels)))
    gas_levels = list(map(lambda x: order_gas[x], gas_sort))
    # --- create target area informations
    if ('LV' in power_levels) or ('LP' in gas_levels):
        roads, roads_plot, buildings, landuse = True, True, True, True
    elif ('MV' in power_levels) or ('MP' in gas_levels):
        roads, roads_plot, buildings, landuse = True, True, False, True
    else:  # for EHV, HV and HP
        roads, roads_plot, buildings, landuse = False, False, False, True
    file_exists, file_name = target_area(grid_data, power_levels=power_levels,
                                         gas_levels=gas_levels, postalcode=postalcode,
                                         town_name=town_name, federal_state=federal_state,
                                         own_area=own_area, buffer=0, roads=roads,
                                         roads_plot=roads_plot, buildings=buildings,
                                         landuse=landuse).target()
    if not file_exists:
        # create extended grid area to combine not connected areas
        if combine_areas:
            # save origin area
            origin_area = grid_data.area
            # hier dann die erstellung über funktion
            combined_area = create_interim_area(grid_data.area)
        # --- create desired power grid levels
        for level in power_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == 'EHV':
                create_ehv_topology(grid_data)
            elif level == 'HV':
                create_hv_topology(grid_data)
            elif level == 'MV':
                create_mv_topology(grid_data)
            elif level == 'LV':
                create_lv_topology(grid_data)
            else:
                print('no voltage level was choosen or their is a failure in the input value.')
                print(f'the input for the power levels was: {power_levels}')
                print('---------------------------------------------------')
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # create power grid components
        if power_levels:
            power_components(grid_data)
        # --- create desired gas grid levels
        for level in gas_levels:
            # temporary extend grid area to combine not connected areas
            if level in combine_areas:
                # temporary use of extended grid area
                grid_data.area = combined_area
            if level == 'HP':
                create_hp_topology(grid_data)
            elif level == 'MP':
                create_mp_topology(grid_data)
            elif level == 'LP':
                create_lp_topology(grid_data)
            else:
                print('no gas level was choosen or their is a failure in the input value.')
                print(f'the input for the gas levels was: {gas_levels}')
                print('-----------------------------------------------')
            # replace grid area with the origin one for further steps
            if level in combine_areas:
                grid_data.area = origin_area
        # create gas grid components
        if gas_levels:
            gas_components(grid_data)
    else:
        # read dataset from archiv
        grid_data = from_archiv(f'{file_name}.h5')

    # create dave output folder on desktop for DaVe dataset, plotting and converted model
    print('Save DaVe dataset, plots and converted grid models at the following path:')
    print(dave_output_dir)
    print('-----------------------------------------------------------------------')
    if not os.path.exists(dave_output_dir):
        os.makedirs(dave_output_dir)

    # save DaVe dataset to archiv and also in the output folder
    if not grid_data.target_input.iloc[0].typ == 'own area':
        # Vorrübergehend aus für testzwecke
        """
        print('Save DaVe dataset to archiv')
        print('---------------------------')
        # save dataset to archiv
        file_name = to_archiv(grid_data)
        # copy file from archiv folder to output folder
        archiv_file_path = dave_dir + '\\datapool\\dave_archiv\\' + f'{file_name}.h5'
        output_file_path = dave_output_dir + '\\' + f'{file_name}.h5'
        if os.path.exists(archiv_file_path):
            shutil.copyfile(archiv_file_path, output_file_path)
        """
    else:
        write_dataset(grid_data, dataset_path=dave_output_dir+'\\'+'dave_dataset.h5')

    # plot informations
    if plot:
        plot_target_area(grid_data)
        plot_grid_data(grid_data)
        plot_landuse(grid_data)

    # convert into pandapower and pandapipes
    if convert and power_levels:
        net_power = create_power_grid(grid_data)
        net_power = power_processing(net_power, opt_model=opt_model)
        # save grid model in the dave output folder
        file_path = dave_output_dir + '\\dave_power_grid.json'  # hier fehlt noch eine richtige funktion, wegen dem geometrien evt io_pandapower
        pp.to_json(net_power, file_path)
    else:
        net_power = None
    if convert and gas_levels:
        net_gas = create_gas_grid(grid_data)
        net_gas = gas_processing(net_gas)
    else:
        net_gas = None

    # return
    if net_power and net_gas:
        return grid_data, net_power, net_gas
    elif net_power:
        return grid_data, net_power
    elif net_gas:
        return grid_data, net_gas
    else:
        return grid_data
