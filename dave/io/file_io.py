import json
import os
import geopandas as gpd
import pandas as pd
from pandapower import to_json, from_json
from shapely.wkb import loads, dumps
from shapely.geometry import Point, LineString, MultiLineString

import dave.create
from dave.settings import dave_settings
from dave.datapool import get_data_path
from dave.io.convert_format import wkb_to_wkt, wkt_to_wkb, wkt_to_wkb_dataset
from dave.io.io_utils import archiv_inventory, DaVeJSONEncoder, encrypt_string
from dave.dave_structure import davestructure


def to_json(grid_data, file_path=None, encryption_key=None):
    """
    This function converts the DaVe dataset into the JSON format.
    Input:
        grid data
        file_path - absoulut path of the file. If None is given the function returns a JSON string
    """
    # convert geometric data in dave dataset
    grid_data_geo = wkt_to_wkb_dataset(grid_data)
    # convert DaVe dataset into a json string with custom encoder
    json_string = json.dumps(grid_data_geo, cls=DaVeJSONEncoder, indent=2)
    # encrypt json string
    if encryption_key is not None:
        json_string = encrypt_string(json_string, encryption_key)
    # only return json string
    if file_path is None:
        return json_string
    # save json string at given file path
    if hasattr(file_path, 'write'):
        file_path.write(json_string)
    else:
        with open(file_path, "w"):
            file_path.write(json_string)


def from_hdf(dataset_path):
    """
    This functions reads a dave dataset in HDF5 format from a user given path

    Output  grid_data - dave dataset

    Example  grid_data = read_dataset(dataset_path)
    """
    crs = dave_settings()['crs_main']
    # check if path exist
    if os.path.exists(dataset_path):
        # create empty dave dataset
        grid_data = dave.create.create_empty_dataset()
        # open hdf file
        file = pd.HDFStore(dataset_path)
        # --- create dave dataset from archiv file
        for key in file.keys():
            # read data from file and convert geometry
            data = file.get(key)
            if 'geometry' in data.keys():
                data = wkb_to_wkt(data, crs)
            if not data.empty:
                # seperate the keys
                key_parts = key[1:].split('/')
                # assign data to the dave dataset
                if len(key_parts) == 1:
                    if key_parts[0] == 'dave_version':
                        grid_data.dave_version = data['dave_version'][0]
                    else:
                        grid_data[key_parts[0]] = grid_data[key_parts[0]].append(data)
                elif len(key_parts) == 2:
                    grid_data[key_parts[0]][key_parts[1]] = grid_data[
                        key_parts[0]][key_parts[1]].append(data)
                elif len(key_parts) == 3:
                    grid_data[key_parts[0]][key_parts[1]][key_parts[2]] = grid_data[
                        key_parts[0]][key_parts[1]][key_parts[2]].append(data)
        # close file
        file.close()
        return grid_data
    else:
        print('Their is no suitable file at the given path')


def to_hdf(grid_data, dataset_path):
    """
    This functions stores a dave dataset at a given path in the HDF5 format
    """
    # create hdf file
    file = pd.HDFStore(dataset_path)
    # go trough the dave dataset keys and save each data in the hdf5 file
    for key in grid_data.keys():
        if isinstance(grid_data[key], davestructure):
            for key_sec in grid_data[key].keys():
                if isinstance(grid_data[key][key_sec], davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if isinstance(grid_data[key][key_sec][key_trd], gpd.GeoDataFrame):
                            file.put(f'/{key}/{key_sec}/{key_trd}',
                                     wkt_to_wkb(grid_data[key][key_sec][key_trd]))
                elif isinstance(grid_data[key][key_sec], gpd.GeoDataFrame):
                    file.put(f'/{key}/{key_sec}', wkt_to_wkb(grid_data[key][key_sec]))
                elif isinstance(grid_data[key][key_sec], gpd.GeoSeries):
                    if not grid_data[key][key_sec].empty:
                        data = pd.DataFrame({'geometry': grid_data[key][key_sec]})
                        data['geometry'] = data.geometry.apply(dumps)
                        file.put(f'/{key}/{key_sec}', data)
                elif isinstance(grid_data[key][key_sec], pd.DataFrame):
                    file.put(f'/{key}/{key_sec}', grid_data[key][key_sec])
        elif isinstance(grid_data[key], gpd.GeoDataFrame):
            file.put(f'/{key}', wkt_to_wkb(grid_data[key]))
        elif isinstance(grid_data[key], pd.DataFrame):
            file.put(f'/{key}', grid_data[key])
        elif isinstance(grid_data[key], str):
            file.put(f'/{key}', pd.DataFrame({key: grid_data[key]}, index=[0]))
    # close file
    file.close()


def from_archiv(dataset_name):
    """
    This functions reads a dave dataset from the dave internal archiv
    """
    # check if file exist
    files_in_archiv = os.listdir(get_data_path(dirname='dave_archiv'))
    if dataset_name in files_in_archiv:
        grid_data = from_hdf(get_data_path(dataset_name, 'dave_archiv'))
        return grid_data
    else:
        print('The requested file is not found in the dave archiv')


def to_archiv(grid_data):
    """
    This functions stores a dave dataset in the dave internal archiv
    """
    # check if file already exists and create file name for archiv
    file_exists, file_name = archiv_inventory(grid_data)
    # create archive file if the dataset does not exists in the archiv
    if not file_exists:
        to_hdf(grid_data, get_data_path(f'{file_name}.h5', 'dave_archiv'))
    else:
        print('The dataset you tried to save already exist in the DaVe archiv'
              f' with the name "{file_name}"')
    return file_name


def pp_to_json(net, file_path):
    """
    This functions converts a pandapower model into a json file
    """
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, Point), net.bus.geometry))):
        net.bus['geometry'] = net.bus.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, (LineString, MultiLineString)),
                                           net.line.geometry))):
        net.line['geometry'] = net.line.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, Point), net.trafo.geometry))):
        net.trafo['geometry'] = net.trafo.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, Point), net.gen.geometry))):
        net.gen['geometry'] = net.gen.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, Point), net.sgen.geometry))):
        net.sgen['geometry'] = net.sgen.geometry.apply(lambda x: dumps(x, hex=True))
    # convert pp model to json and save the file
    to_json(net, filename=file_path)


def json_to_pp(file_path):
    """
    This functions converts a json file into a pandapower model
    """
    # read json file and convert to pp model
    net = from_json(file_path)
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, str), net.bus.geometry))):
        net.bus['geometry'] = net.bus.geometry.apply(lambda x: loads(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, str), net.line.geometry))):
        net.line['geometry'] = net.line.geometry.apply(lambda x: loads(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, str), net.trafo.geometry))):
        net.trafo['geometry'] = net.trafo.geometry.apply(lambda x: loads(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, str), net.gen.geometry))):
        net.gen['geometry'] = net.gen.geometry.apply(lambda x: loads(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, str), net.sgen.geometry))):
        net.sgen['geometry'] = net.sgen.geometry.apply(lambda x: loads(x, hex=True))
    return net
