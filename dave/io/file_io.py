# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json
import os
from functools import partial

import geopandas as gpd
import pandapipes as ppi
import pandapower as pp
import pandas as pd
from pandapower.io_utils import (
    PPJSONDecoder,
    PPJSONEncoder,
    decrypt_string,
    encrypt_string,
    pp_hook,
)
from shapely.geometry import LineString, MultiLineString, Point
from shapely.wkb import dumps, loads

import dave.create as create
from dave.dave_structure import davestructure
from dave.io.convert_format import change_empty_gpd, wkb_to_wkt, wkt_to_wkb
from dave.io.io_utils import FromSerializableRegistryDaVe, archiv_inventory, isinstance_partial
from dave.settings import dave_settings
from dave.toolbox import get_data_path


# --- JSON
def from_json(file_path, encryption_key=None):
    """
    Load a dave dataset from a JSON file.
    """
    if hasattr(file_path, "read"):
        json_string = file_path.read()
    elif not os.path.isfile(file_path):
        raise UserWarning("File {} does not exist!!".format(file_path))
    else:
        with open(file_path) as file:
            json_string = file.read()
    # check if it is a json string in DAVE structure
    json_type = json.loads(json_string)["_module"]
    if json_type == "dave.dave_structure":  # !!! Fehler??
        return from_json_string(json_string, encryption_key=encryption_key)
    elif json_type == "pandapower.auxiliary":
        print("A pandapower network is given as input and will be convertert in pandapower format")
        return pp.from_json(file_path)
    elif json_type == "ppi":
        print("A pandapipes network is given as input and will be convertert in pandapipes format")
        return ppi.from_json(file_path)
    else:
        raise UserWarning("The given json file is not a DAVE dataset")


def from_json_string(json_string, encryption_key=None):
    """
    Load a dave dataset from a JSON string.
    """
    if encryption_key is not None:
        json_string = decrypt_string(json_string, encryption_key)

    dataset = json.loads(
        json_string,
        cls=PPJSONDecoder,
        object_hook=partial(pp_hook, registry_class=FromSerializableRegistryDaVe),
    )
    return dataset


def to_json(grid_data, file_path=None, encryption_key=None):
    """
    This function saves a DaVe dataset in JSON format.
    INPUT:
        **grid_data** (dict) - all Informations about the grid area
        **file_path** (str , default None) - absoulut path where the JSON file will be stored. If
                                             None is given the function returns only a JSON string
        **encrytion_key** (string, None) - If given, the DaVe dataset is stored as an encrypted \
            json string
    OUTPUT:
        **file** (json) - the dave dataset in JSON format

    """
    # convert all empty geopandas objects to empty pandas objects
    grid_data = change_empty_gpd(grid_data)
    # convert DaVe dataset into a json string with custom encoder
    json_string = json.dumps(
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
def from_hdf(dataset_path):
    """
    This functions reads a dave dataset in HDF5 format from a user given path

    Output  grid_data - dave dataset

    Example  grid_data = read_dataset(dataset_path)
    """
    crs = dave_settings()["crs_main"]
    # check if path exist
    if os.path.exists(dataset_path):
        # create empty dave dataset
        grid_data = create.create_empty_dataset()
        # open hdf file
        file = pd.HDFStore(dataset_path)
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
                            file.put(
                                f"/{key}/{key_sec}/{key_trd}",
                                wkt_to_wkb(grid_data[key][key_sec][key_trd]),
                            )
                elif isinstance(grid_data[key][key_sec], gpd.GeoDataFrame):
                    file.put(f"/{key}/{key_sec}", wkt_to_wkb(grid_data[key][key_sec]))
                elif (
                    isinstance(grid_data[key][key_sec], gpd.GeoSeries)
                    and not grid_data[key][key_sec].empty
                ):
                    data = pd.DataFrame({"geometry": grid_data[key][key_sec]})
                    data["geometry"] = data.geometry.apply(dumps)
                    file.put(f"/{key}/{key_sec}", data)
                elif isinstance(grid_data[key][key_sec], pd.DataFrame):
                    file.put(f"/{key}/{key_sec}", grid_data[key][key_sec])
        elif isinstance(grid_data[key], gpd.GeoDataFrame):
            file.put(f"/{key}", wkt_to_wkb(grid_data[key]))
        elif isinstance(grid_data[key], pd.DataFrame):
            file.put(f"/{key}", grid_data[key])
        elif isinstance(grid_data[key], str):
            file.put(f"/{key}", pd.DataFrame({key: grid_data[key]}, index=[0]))
    # close file
    file.close()


# --- geopackage (GPKG)
def to_gpkg(grid_data, dataset_path):
    """
    This functions stores a dave dataset at a given path in the geopackage format
    """
    # go trough the dave dataset keys and save each data in the gpkg file
    for key in grid_data.keys():
        if isinstance(grid_data[key], davestructure):
            for key_sec in grid_data[key].keys():
                if isinstance(grid_data[key][key_sec], davestructure):
                    for key_trd in grid_data[key][key_sec].keys():
                        if (
                            isinstance(grid_data[key][key_sec][key_trd], gpd.GeoDataFrame)
                            and not grid_data[key][key_sec][key_trd].empty
                        ):
                            grid_data[key][key_sec][key_trd].to_file(
                                dataset_path, layer=f"{key}/{key_sec}/{key_trd}", driver="GPKG"
                            )
                elif (
                    isinstance(grid_data[key][key_sec], gpd.GeoDataFrame)
                    and not grid_data[key][key_sec].empty
                ):
                    grid_data[key][key_sec].to_file(
                        dataset_path, layer=f"{key}/{key_sec}", driver="GPKG"
                    )
                elif (
                    isinstance(grid_data[key][key_sec], gpd.GeoSeries)
                    and not grid_data[key][key_sec].empty
                ):
                    data = gpd.GeoDataFrame({"geometry": grid_data[key][key_sec]})
                    data.to_file(dataset_path, layer=f"{key}/{key_sec}", driver="GPKG")
        elif isinstance(grid_data[key], gpd.GeoDataFrame) and not grid_data[key].empty:
            grid_data[key].to_file(dataset_path, layer=f"{key}", driver="GPKG")


# --- Archiv
def from_archiv(dataset_name):
    """
    This functions reads a dave dataset from the dave internal archiv
    """
    # check if file exist
    files_in_archiv = os.listdir(get_data_path(dirname="dave_archiv"))
    if dataset_name in files_in_archiv:
        grid_data = from_hdf(get_data_path(dataset_name, "dave_archiv"))
        return grid_data
    else:
        print("The requested file is not found in the dave archiv")


def to_archiv(grid_data):
    """
    This functions stores a dave dataset in the dave internal archiv
    """
    # check if file already exists and create file name for archiv
    file_exists, file_name = archiv_inventory(grid_data)
    # create archive file if the dataset does not exists in the archiv
    if not file_exists:
        to_hdf(grid_data, get_data_path(f"{file_name}.h5", "dave_archiv"))
    else:
        print(
            "The dataset you tried to save already exist in the DaVe archiv"
            f' with the name "{file_name}"'
        )
    return file_name


# --- pandapower
def pp_to_json(net, file_path):
    """
    This functions converts a pandapower model into a json file
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
    # convert pp model to json and save the file
    pp.to_json(net, filename=file_path)


def json_to_pp(file_path):
    """
    This functions converts a json file into a pandapower model
    """
    # read json file and convert to pp model
    net = pp.from_json(file_path)
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
def ppi_to_json(net, file_path):
    """
    This functions converts a pandapipes model into a json file
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
    ppi.to_json(net, filename=file_path)


def json_to_ppi(file_path):
    """
    This functions converts a json file into a pandapipes model
    """
    # read json file and convert to pp model
    net = ppi.from_json(file_path)
    # convert geometry
    if not net.junction.empty and all(
        list(map(lambda x: isinstance(x, str), net.junction.geometry))
    ):
        net.junction["geometry"] = net.junction.geometry.apply(lambda x: loads(x, hex=True))
    if not net.pipe.empty and all(list(map(lambda x: isinstance(x, str), net.pipe.geometry))):
        net.pipe["geometry"] = net.pipe.geometry.apply(lambda x: loads(x, hex=True))
    return net
