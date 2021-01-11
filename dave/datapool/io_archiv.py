import os
import copy
import geopandas as gpd
import pandas as pd
from shapely.wkb import loads, dumps

import dave.create
from dave.datapool import get_data_path


def _convert_from_archiv_data(archiv_file, key):
    """
    This function converts the geographical informations into geographical objects and creats a
    GeoDataFrame
    """
    data = archiv_file.get(key)
    if (not data.empty) and ('geometry' in data.keys()):
        data['geometry'] = data.geometry.apply(loads)
    data = gpd.GeoDataFrame(data)
    return data


def _convert_to_archiv_data(data_key):
    """
    This function converts the geographical objects into a string and creats a DataFrame
    """
    data = copy.deepcopy(data_key)
    if not data.empty:
        if 'geometry' in data.keys():
            data['geometry'] = data.geometry.apply(dumps)
        data = pd.DataFrame(data)
    else:
        data = pd.DataFrame([])
    return data


def archiv_inventory(grid_data, read_only=False):
    """
    This function check if a the dave archiv already contain the dataset.
    Otherwise the dataset name and possibly the inventory list were created
    """
    # check if inventory file exists
    inventory_path = get_data_path('inventory.csv', 'dave_archiv')
    # dataset parameters
    target_input = grid_data.target_input.iloc[0]
    postalcode = target_input.data if target_input.typ == 'postalcode' else 'None'
    town_name = target_input.data if target_input.typ == 'town name' else 'None'
    federal_state = target_input.data if target_input.typ == 'federal state' else 'None'
    if os.path.isfile(inventory_path):
        # read inventory file
        inventory_list = pd.read_csv(inventory_path)
        # create dataset file
        dataset_file = pd.DataFrame({'postalcode': str(postalcode),
                                     'town_name': str(town_name),
                                     'federal_state': str(federal_state),
                                     'power_levels': str(target_input.power_levels),
                                     'gas_levels': str(target_input.gas_levels),
                                     'dave_version': grid_data.dave_version},
                                    index=[0])
        # check if archiv already contain dataset
        inventory_check = inventory_list.drop(columns=['id'])
        inventory_check_res = inventory_check == dataset_file.iloc[0]
        inventory_index = inventory_check_res[inventory_check_res.all(axis='columns')].index
        if not inventory_index.empty:
            # in this case the dataset already exists in the archiv
            file_id = inventory_list.loc[inventory_index[0]].id
            file_name = f'dataset_{file_id}'
            return True, file_name
        else:
            # --- in this case the dataset don't exist already in the archiv
            # set file id and name
            file_id = inventory_list.tail(1).iloc[0].id+1
            file_name = f'dataset_{file_id}'
            if not read_only:
                # create inventory entry
                dataset_entry = pd.DataFrame({'id': file_id,
                                              'postalcode': [postalcode],
                                              'town_name': [town_name],
                                              'federal_state': [federal_state],
                                              'power_levels': [target_input.power_levels],
                                              'gas_levels': [target_input.gas_levels],
                                              'dave_version': grid_data.dave_version})
                inventory_list = inventory_list.append(dataset_entry)
                inventory_list.to_csv(inventory_path, index=False)
            return False, file_name
    else:
        # --- archiv don't contain the dataset because it's empty
        # set file id and name
        file_id = 1
        file_name = f'dataset_{file_id}'
        if not read_only:
            # create inventory file
            inventory_list = pd.DataFrame({'id': file_id,
                                           'postalcode': [postalcode],
                                           'town_name': [town_name],
                                           'federal_state': [federal_state],
                                           'power_levels': [target_input.power_levels],
                                           'gas_levels': [target_input.gas_levels],
                                           'dave_version': grid_data.dave_version})
            inventory_list.to_csv(inventory_path, index=False)
        return False, file_name


def to_archiv(grid_data):
    """
    This functions stores a dave dataset in the dave internal archiv
    """
    # check if file already exists and create file name for archiv
    file_exists, file_name = archiv_inventory(grid_data)
    # create archive file if the dataset does not exists in the archiv
    if not file_exists:
        # --- create file
        archiv_file = pd.HDFStore(get_data_path(f'{file_name}.h5', 'dave_archiv'))
        # area
        area = _convert_to_archiv_data(grid_data.area)
        archiv_file.put('/area', area)
        # target input
        archiv_file.put('/target_input', grid_data.target_input)
        # buildings
        archiv_file.put('/buildings/commercial',
                        _convert_to_archiv_data(grid_data.buildings.commercial))
        archiv_file.put('/buildings/for_living',
                        _convert_to_archiv_data(grid_data.buildings.for_living))
        archiv_file.put('/buildings/other', _convert_to_archiv_data(grid_data.buildings.other))
        # roads
        archiv_file.put('/roads/roads', _convert_to_archiv_data(grid_data.roads.roads))
        archiv_file.put('/roads/roads_plot', _convert_to_archiv_data(grid_data.roads.roads_plot))
        road_junctions = copy.deepcopy(grid_data.roads.road_junctions)
        if not road_junctions.empty:
            road_junctions = pd.DataFrame({'geometry': road_junctions})
            road_junctions['geometry'] = road_junctions.geometry.apply(dumps)
        else:
            road_junctions = pd.DataFrame([])
        archiv_file.put('/roads/road_junctions', road_junctions)
        # landuse
        archiv_file.put('/landuse', _convert_to_archiv_data(grid_data.landuse))
        # ehv data
        archiv_file.put('/ehv_data/ehv_lines',
                        _convert_to_archiv_data(grid_data.ehv_data.ehv_lines))
        archiv_file.put('/ehv_data/ehv_nodes',
                        _convert_to_archiv_data(grid_data.ehv_data.ehv_nodes))
        archiv_file.put('/ehv_data/ehv_substations',
                        _convert_to_archiv_data(grid_data.ehv_data.ehv_substations))
        # hv data
        archiv_file.put('/hv_data/hv_nodes', _convert_to_archiv_data(grid_data.hv_data.hv_nodes))
        archiv_file.put('/hv_data/hv_lines', _convert_to_archiv_data(grid_data.hv_data.hv_lines))
        # mv data
        archiv_file.put('/mv_data/mv_nodes', _convert_to_archiv_data(grid_data.mv_data.mv_nodes))
        archiv_file.put('/mv_data/mv_lines', _convert_to_archiv_data(grid_data.mv_data.mv_lines))
        # lv data
        archiv_file.put('/lv_data/lv_nodes', _convert_to_archiv_data(grid_data.lv_data.lv_nodes))
        archiv_file.put('/lv_data/lv_lines', _convert_to_archiv_data(grid_data.lv_data.lv_lines))
        # components_power
        archiv_file.put('/components_power/conventional_powerplants',
                        _convert_to_archiv_data(
                            grid_data.components_power.conventional_powerplants))
        archiv_file.put('/components_power/renewable_powerplants',
                        _convert_to_archiv_data(grid_data.components_power.renewable_powerplants))
        archiv_file.put('/components_power/loads',
                        _convert_to_archiv_data(grid_data.components_power.loads))
        archiv_file.put('/components_power/transformers/ehv_ehv',
                        _convert_to_archiv_data(grid_data.components_power.transformers.ehv_ehv))
        archiv_file.put('/components_power/transformers/ehv_hv',
                        _convert_to_archiv_data(grid_data.components_power.transformers.ehv_hv))
        archiv_file.put('/components_power/transformers/hv_mv',
                        _convert_to_archiv_data(grid_data.components_power.transformers.hv_mv))
        archiv_file.put('/components_power/transformers/mv_lv',
                        _convert_to_archiv_data(grid_data.components_power.transformers.mv_lv))
        # hp data
        archiv_file.put('/hp_data/hp_junctions',
                        _convert_to_archiv_data(grid_data.hp_data.hp_junctions))
        archiv_file.put('/hp_data/hp_pipes', _convert_to_archiv_data(grid_data.hp_data.hp_pipes))
        # mp data
        archiv_file.put('/mp_data/mp_junctions',
                        _convert_to_archiv_data(grid_data.mp_data.mp_junctions))
        archiv_file.put('/mp_data/mp_pipes', _convert_to_archiv_data(grid_data.mp_data.mp_pipes))
        # lp data
        archiv_file.put('/lp_data/lp_junctions',
                        _convert_to_archiv_data(grid_data.lp_data.lp_junctions))
        archiv_file.put('/lp_data/lp_pipes', _convert_to_archiv_data(grid_data.lp_data.lp_pipes))
        # components gas
        archiv_file.put('/components_gas/sinks',
                        _convert_to_archiv_data(grid_data.components_gas.sinks))
        archiv_file.put('/components_gas/sources',
                        _convert_to_archiv_data(grid_data.components_gas.sources))
        # dave version
        archiv_file.put('/dave_version',
                        pd.DataFrame({'dave_version': grid_data.dave_version}, index=[0]))
        # close file
        archiv_file.close()
    else:
        print('The dataset you tried to save already exist in the DaVe archiv'
              f' with the name "{file_name}"')
    return file_name


def from_archiv(dataset_name):
    """
    This functions reads a dave dataset from the dave internal archiv
    """
    crs = 'EPSG:4326'
    # check if file exist
    files_in_archiv = os.listdir(get_data_path(dirname='dave_archiv'))
    if dataset_name in files_in_archiv:
        # read data
        archiv_file = pd.HDFStore(get_data_path(dataset_name, 'dave_archiv'))
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # --- create dave dataset from archiv file
        # area
        grid_data.area = grid_data.area.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/area'), crs=crs))
        # target input
        grid_data.target_input = grid_data.target_input.append(archiv_file.get('/target_input'))
        # buildings
        grid_data.buildings.commercial = grid_data.buildings.commercial.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/buildings/commercial'),
                             crs=crs))
        grid_data.buildings.for_living = grid_data.buildings.for_living.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/buildings/for_living'),
                             crs=crs))
        grid_data.buildings.other = grid_data.buildings.other.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/buildings/other'), crs=crs))
        # roads
        grid_data.roads.roads = grid_data.roads.roads.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/roads/roads'), crs=crs))
        grid_data.roads.roads_plot = grid_data.roads.roads_plot.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/roads/roads_plot'), crs=crs))
        road_junctions = _convert_from_archiv_data(archiv_file, '/roads/road_junctions')
        if not road_junctions.empty:
            road_junctions = road_junctions['geometry']
            road_junctions = gpd.GeoSeries(road_junctions, crs=crs)
            grid_data.roads.road_junctions = grid_data.roads.road_junctions.append(road_junctions)
        # landuse
        grid_data.landuse = grid_data.landuse.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/landuse'), crs=crs))
        # ehv data
        grid_data.ehv_data.ehv_lines = grid_data.ehv_data.ehv_lines.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/ehv_data/ehv_lines'),
                             crs=crs))
        grid_data.ehv_data.ehv_nodes = grid_data.ehv_data.ehv_nodes.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/ehv_data/ehv_nodes'),
                             crs=crs))
        grid_data.ehv_data.ehv_substations = grid_data.ehv_data.ehv_substations.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/ehv_data/ehv_substations'),
                             crs=crs))
        # hv data
        grid_data.hv_data.hv_nodes = grid_data.hv_data.hv_nodes.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/hv_data/hv_nodes'), crs=crs))
        grid_data.hv_data.hv_lines = grid_data.hv_data.hv_lines.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/hv_data/hv_lines'), crs=crs))
        # mv data
        grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/mv_data/mv_nodes'), crs=crs))
        grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/mv_data/mv_lines'), crs=crs))
        # lv data
        grid_data.lv_data.lv_nodes = grid_data.lv_data.lv_nodes.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/lv_data/lv_nodes'), crs=crs))
        grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/lv_data/lv_lines'), crs=crs))
        # components_power
        grid_data.components_power.conventional_powerplants = \
            grid_data.components_power.conventional_powerplants.append(
                gpd.GeoDataFrame(_convert_from_archiv_data(
                    archiv_file, '/components_power/conventional_powerplants'), crs=crs))
        grid_data.components_power.renewable_powerplants = \
            grid_data.components_power.renewable_powerplants.append(gpd.GeoDataFrame(
                _convert_from_archiv_data(archiv_file, '/components_power/renewable_powerplants'),
                crs=crs))
        grid_data.components_power.loads = grid_data.components_power.loads.append(
            gpd.GeoDataFrame(_convert_from_archiv_data(archiv_file, '/components_power/loads'),
                             crs=crs))
        grid_data.components_power.transformers.ehv_ehv = \
            grid_data.components_power.transformers.ehv_ehv.append(gpd.GeoDataFrame(
                _convert_from_archiv_data(archiv_file, '/components_power/transformers/ehv_ehv'),
                crs=crs))
        grid_data.components_power.transformers.ehv_hv = \
            grid_data.components_power.transformers.ehv_hv.append(gpd.GeoDataFrame(
                _convert_from_archiv_data(archiv_file, '/components_power/transformers/ehv_hv'),
                crs=crs))
        grid_data.components_power.transformers.hv_mv = \
            grid_data.components_power.transformers.hv_mv.append(gpd.GeoDataFrame(
                _convert_from_archiv_data(archiv_file, '/components_power/transformers/hv_mv'),
                crs=crs))
        grid_data.components_power.transformers.mv_lv = \
            grid_data.components_power.transformers.mv_lv.append(gpd.GeoDataFrame(
                _convert_from_archiv_data(archiv_file, '/components_power/transformers/mv_lv'),
                crs=crs))
        # hp data
        grid_data.hp_data.hp_junctions = grid_data.hp_data.hp_junctions.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/hp_data/hp_junctions'), crs=crs))
        grid_data.hp_data.hp_pipes = grid_data.hp_data.hp_pipes.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/hp_data/hp_pipes'), crs=crs))
        # mp data
        grid_data.mp_data.mp_junctions = grid_data.mp_data.mp_junctions.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/mp_data/mp_junctions'), crs=crs))
        grid_data.mp_data.mp_pipes = grid_data.mp_data.mp_pipes.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/mp_data/mp_pipes'), crs=crs))
        # lp data
        grid_data.lp_data.lp_junctions = grid_data.lp_data.lp_junctions.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/lp_data/lp_junctions'), crs=crs))
        grid_data.lp_data.lp_pipes = grid_data.lp_data.lp_pipes.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/lp_data/lp_pipes'), crs=crs))
        # components gas
        grid_data.components_gas.sinks = grid_data.components_gas.sinks.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/components_gas/sinks'), crs=crs))
        grid_data.components_gas.sources = grid_data.components_gas.sources.append(gpd.GeoDataFrame(
            _convert_from_archiv_data(archiv_file, '/components_gas/sources'), crs=crs))
        # dave version
        grid_data.dave_version = archiv_file.get('/dave_version')['dave_version'][0]
        # close file
        archiv_file.close()
        return grid_data
    else:
        print('The requested file is not found in the dave archiv')
