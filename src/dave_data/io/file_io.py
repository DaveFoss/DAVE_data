# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from functools import partial
from json import dumps as json_dumps
from json import loads as json_loads
from os.path import exists, isfile

from geopandas import GeoDataFrame, GeoSeries

from pandas import DataFrame, HDFStore
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.wkb import dumps, loads

from dave_data.dave_structure import create_empty_dataset, davestructure
from dave_data.io.convert_format import change_empty_gpd, wkb_to_wkt, wkt_to_wkb
from dave_data.io.io_utils import FromSerializableRegistryDaVe, isinstance_partial
from dave_data.settings import dave_settings


# --- JSON
def from_json(file_path, encryption_key=None):
    """
    Load a dave dataset from a JSON file.

    INPUT:
        **file_path** (str ) - absoulut path where the JSON file will be stored. If None is given \
            the function returns only a JSON string
        **encrytion_key** (string, None) - If given, the DAVE dataset is stored as an encrypted \
            json string
    OUTPUT:
        **file** (json) - the DAVE dataset in JSON format

    """
    if hasattr(file_path, "read"):
        json_string = file_path.read()
    elif not isfile(file_path):
        raise UserWarning("File {} does not exist!!".format(file_path))
    else:
        with open(file_path) as file:
            json_string = file.read()
    # check if it is a json string in DAVE structure
    json_type = json_loads(json_string)["_module"]
    if json_type in ["dave.dave_structure", "dave_client.dave_structure"]:
        return from_json_string(json_string, encryption_key=encryption_key)
    elif json_type == "pandapower.auxiliary":
        print("A pandapower network is given as input and will be convertert in pandapower format")
        return from_json_pp(file_path)
    elif json_type == "ppi":
        print("A pandapipes network is given as input and will be convertert in pandapipes format")
        return from_json_ppi(file_path)
    else:
        raise UserWarning("The given json file is not a DAVE dataset")


def from_json_string(json_string, encryption_key=None):
    """
    Load a dave dataset from a JSON string.

    INPUT:
        **json_string** (str ) - json string
        **encrytion_key** (string, None) - If given, the DAVE dataset is stored as an encrypted \
            json string
    OUTPUT:
        **test** (json) - the DAVE dataset in JSON format
    """
    if encryption_key is not None:
        json_string = decrypt_string(json_string, encryption_key)

    dataset = json_loads(
        json_string,
        cls=PPJSONDecoder,
        object_hook=partial(pp_hook, registry_class=FromSerializableRegistryDaVe),
    )
    return dataset


def to_json(grid_data, file_path=None, encryption_key=None):
    """
    This function saves a DAVE dataset in JSON format.

    INPUT:
        **grid_data** (attr Dict) - DAVE Dataset
        **file_path** (str , None) - absoulut path where the JSON file will be stored. If None is \
            given the function returns only a JSON string
        **encrytion_key** (string, None) - If given, the DaVe dataset is stored as an encrypted \
            json string
    OUTPUT:
        **json_string** (Str) - The Data converted to a json string

    """
    # convert all empty geopandas objects to empty pandas objects
    grid_data = change_empty_gpd(grid_data)
    # convert DaVe dataset into a json string with custom encoder
    json_string = json_dumps(
        grid_data, cls=PPJSONEncoder, indent=2, isinstance_func=isinstance_partial
    )
    # encrypt json string
    if encryption_key is not None:
        json_string = encrypt_string(json_string, encryption_key)
    # only return json string
    if file_path is None:
        return json_string
    if hasattr(file_path, "write"):
        file_path.write(json_string)
    else:
        with open(file_path, "w") as file:
            file.write(json_string)


# --- HDF5
def from_hdf(file_path):
    """
    This functions reads a dave dataset given in HDF5 format from a user given path

    INPUT:
        **file_path** (str ) - absoulut path where the HDF5 file will be stored.

    OUTPUT:
        **grid_data** (attr Dict) - DAVE Dataset

    Example  grid_data = from_hdf(file_path)
    """
    crs = dave_settings["crs_main"]
    # check if path exist
    if exists(file_path):
        # create empty dave dataset
        grid_data = create_empty_dataset()
        # open hdf file
        file = HDFStore(file_path)
        # --- create dave dataset from archiv file
        for key in file.keys():
            # read data from file and convert geometry
            data = file.get(key)
            if "geometry" in data.keys():
                data = wkb_to_wkt(data, crs)
            if not data.empty:
                # seperate the keys
                key_parts = key[1:].split("/")
                # assign data to the dave dataset
                if len(key_parts) == 1:
                    if key_parts[0] == "dave_version":
                        grid_data.dave_version = data["dave_version"][0]
                    else:
                        grid_data[key_parts[0]] = grid_data[key_parts[0]].append(data)
                elif len(key_parts) == 2:
                    # data road junctions has to convert into series object
                    if key_parts[1] == "road_junctions":
                        data = data.geometry
                    grid_data[key_parts[0]][key_parts[1]] = grid_data[key_parts[0]][
                        key_parts[1]
                    ].append(data)
                elif len(key_parts) == 3:
                    grid_data[key_parts[0]][key_parts[1]][key_parts[2]] = grid_data[key_parts[0]][
                        key_parts[1]
                    ][key_parts[2]].append(data)
        # close file
        file.close()
        return grid_data
    else:
        print("Their is no suitable file at the given path")


def to_hdf(grid_data, file_path):
    """
    This functions stores a dave dataset at a given path in the HDF5 format

    INPUT:
        **grid_data** (attr Dict) - DAVE Dataset
        **file_path** (str) - absoulut path where the HDF5 file will be stored.
    """
    # create hdf file
    file = HDFStore(file_path)
    # go trough the dave dataset keys and save each data in the hdf5 file
    for key in grid_data.keys():
        if isinstance(grid_data[key], davestructure):
            for key_sec in grid_data[key].keys():
                if isinstance(grid_data[key][key_sec], davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if isinstance(grid_data[key][key_sec][key_trd], GeoDataFrame):
                            file.put(
                                f"/{key}/{key_sec}/{key_trd}",
                                wkt_to_wkb(grid_data[key][key_sec][key_trd]),
                            )
                elif isinstance(grid_data[key][key_sec], GeoDataFrame):
                    file.put(f"/{key}/{key_sec}", wkt_to_wkb(grid_data[key][key_sec]))
                elif (
                    isinstance(grid_data[key][key_sec], GeoSeries)
                    and not grid_data[key][key_sec].empty
                ):
                    data = DataFrame({"geometry": grid_data[key][key_sec]})
                    data["geometry"] = data.geometry.apply(dumps)
                    file.put(f"/{key}/{key_sec}", data)
                elif isinstance(grid_data[key][key_sec], DataFrame):
                    file.put(f"/{key}/{key_sec}", grid_data[key][key_sec])
        elif isinstance(grid_data[key], GeoDataFrame):
            file.put(f"/{key}", wkt_to_wkb(grid_data[key]))
        elif isinstance(grid_data[key], DataFrame):
            file.put(f"/{key}", grid_data[key])
        elif isinstance(grid_data[key], str):
            file.put(f"/{key}", DataFrame({key: grid_data[key]}, index=[0]))
    # close file
    file.close()


# --- geopackage (GPKG)
def df_lists_to_str(data_df):
    """
    This function checks dataframes if there are any lists included and in the case convert them
    to strings. This is necessary for converting into geopackage format.

    INPUT:
        **data_df** (DataFrame) - Data which includes lists

    Output:
        **data_df** (DataFrame) - Data without including lists

    """
    for col in data_df.columns:
        if any(isinstance(val, list) for val in data_df[col]):
            data_df[col] = data_df[col].apply(lambda x: str(x))
    return data_df


def to_gpkg(grid_data, file_path):
    """
    This functions stores a dave dataset at a given path in the geopackage format

    INPUT:
        **grid_data** (attr Dict) - DAVE Dataset
        **file_path** (str) - absoulut path where the gpkg file will be stored.
    """
    # go trough the dave dataset keys and save each data in the gpkg file
    for key in grid_data.keys():
        # if isinstance(type(grid_data[key]), davestructure):  # TODO: isinstance does not work
        if str(type(grid_data[key])) == str(davestructure):
            for key_sec in grid_data[key].keys():
                # case davestructure
                # if isinstance(grid_data[key][key_sec], davestructure):
                if str(type(grid_data[key][key_sec])) == str(davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if (
                            isinstance(grid_data[key][key_sec][key_trd], GeoDataFrame)
                            and not grid_data[key][key_sec][key_trd].empty
                        ):
                            data = df_lists_to_str(grid_data[key][key_sec][key_trd])
                            data.to_file(
                                file_path, layer=f"{key}/{key_sec}/{key_trd}", driver="GPKG"
                            )
                # case GeoDataFrame
                elif (
                    isinstance(grid_data[key][key_sec], GeoDataFrame)
                    and not grid_data[key][key_sec].empty
                ):
                    data = df_lists_to_str(grid_data[key][key_sec])
                    data.to_file(file_path, layer=f"{key}/{key_sec}", driver="GPKG")
                # case GeoSeries
                elif (
                    isinstance(grid_data[key][key_sec], GeoSeries)
                    and not grid_data[key][key_sec].empty
                ):
                    data = GeoDataFrame({"geometry": grid_data[key][key_sec]})
                    data = df_lists_to_str(data)
                    data.to_file(file_path, layer=f"{key}/{key_sec}", driver="GPKG")
        elif isinstance(grid_data[key], GeoDataFrame) and not grid_data[key].empty:
            data = df_lists_to_str(grid_data[key])
            data.to_file(file_path, layer=f"{key}", driver="GPKG")


# --- pandapower
def pp_to_json(net, file_path):
    """
    This functions converts a pandapower model into a json file in consideration of converting \
    geometry objects to strings

    INPUT:
        **net** (attr Dict) - pandapower network
        **file_path** (str) - absoulut path where the pandapower file will be stored in json format
    """
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, Point), net.bus.geometry))):
        net.bus["geometry"] = net.bus.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.line.empty and all(
        list(map(lambda x: isinstance(x, (LineString, MultiLineString)), net.line.geometry))
    ):
        net.line["geometry"] = net.line.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, Point), net.trafo.geometry))):
        net.trafo["geometry"] = net.trafo.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, Point), net.gen.geometry))):
        net.gen["geometry"] = net.gen.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, Point), net.sgen.geometry))):
        net.sgen["geometry"] = net.sgen.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.substations.empty and all(
        list(map(lambda x: isinstance(x, Polygon), net.substations.geometry))
    ):
        net.substations["geometry"] = net.substations.geometry.apply(lambda x: dumps(x, hex=True))
    # convert pp model to json and save the file
    to_json_pp(net, filename=file_path)


def json_to_pp(file_path):
    """
    This functions converts a json file into a pandapower model in consideration of converting \
    geometry as strings to geometry objects

    INPUT:
        **file_path** (str) - absoulut path where the pandapower file is stored in json format

    OUTPUT:
        **net** (attr Dict) - pandapower network
    """
    # read json file and convert to pp model
    net = from_json_pp(file_path)
    # convert geometry
    if not net.bus.empty and all(list(map(lambda x: isinstance(x, str), net.bus.geometry))):
        net.bus["geometry"] = net.bus.geometry.apply(lambda x: loads(x, hex=True))
    if not net.line.empty and all(list(map(lambda x: isinstance(x, str), net.line.geometry))):
        net.line["geometry"] = net.line.geometry.apply(lambda x: loads(x, hex=True))
    if not net.trafo.empty and all(list(map(lambda x: isinstance(x, str), net.trafo.geometry))):
        net.trafo["geometry"] = net.trafo.geometry.apply(lambda x: loads(x, hex=True))
    if not net.gen.empty and all(list(map(lambda x: isinstance(x, str), net.gen.geometry))):
        net.gen["geometry"] = net.gen.geometry.apply(lambda x: loads(x, hex=True))
    if not net.sgen.empty and all(list(map(lambda x: isinstance(x, str), net.sgen.geometry))):
        net.sgen["geometry"] = net.sgen.geometry.apply(lambda x: loads(x, hex=True))
    return net


# --- pandapipes
def ppi_to_json(net, file_path=None):
    """
    This functions converts a pandapipes model into a json file in consideration of converting \
    geometry objects to strings

    INPUT:
        **net** (attr Dict) - pandapipes network
        **file_path** (str) - absoulut path where the pandapipes file will be stored in json format
    """
    # convert geometry
    if not net.junction.empty and all(
        list(map(lambda x: isinstance(x, Point), net.junction.geometry))
    ):
        net.junction["geometry"] = net.junction.geometry.apply(lambda x: dumps(x, hex=True))
    if not net.pipe.empty and all(
        list(map(lambda x: isinstance(x, (LineString, MultiLineString)), net.pipe.geometry))
    ):
        net.pipe["geometry"] = net.pipe.geometry.apply(lambda x: dumps(x, hex=True))
    # convert ppi model to json and save the file
    if file_path:
        ppi_to_json(net, filename=file_path)
    else:
        net_ppi_json = to_json_ppi(net)
        return net_ppi_json


def json_to_ppi(file_path):
    """
    This functions converts a json file into a pandapipes model in consideration of converting \
    geometry as strings to geometry objects

    INPUT:
        **file_path** (str) - absoulut path where the pandapipes file is stored in json format

    OUTPUT:
        **net** (attr Dict) - pandapipes network
    """
    # read json file and convert to pp model
    net = from_json_ppi(file_path)
    # convert geometry
    if not net.junction.empty and all(
        list(map(lambda x: isinstance(x, str), net.junction.geometry))
    ):
        net.junction["geometry"] = net.junction.geometry.apply(lambda x: loads(x, hex=True))
    if not net.pipe.empty and all(list(map(lambda x: isinstance(x, str), net.pipe.geometry))):
        net.pipe["geometry"] = net.pipe.geometry.apply(lambda x: loads(x, hex=True))
    return net
