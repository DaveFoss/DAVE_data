# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import geopandas as gpd
import pandas as pd
import requests
from pymongo import GEOSPHERE, MongoClient
from shapely.geometry import mapping, shape
from shapely.wkt import loads

from dave.io.convert_format import wkb_to_wkt
from dave.settings import dave_settings


def info_mongo():
    info_mongo = {}
    client = db_client()
    # wirte databases
    for db in list(client.list_databases()):
        if db["name"] not in ["admin", "config", "local"]:
            db_name = client[db["name"]]
            collections = []
            for collection in list(db_name.list_collections()):
                collections.append(collection["name"])
            db["collections"] = collections
            info_mongo[db["name"]] = db
    return info_mongo


def db_availability(collection_name=None):
    # check if the dave database is available
    try:
        requests.get(f"http://{dave_settings()['db_ip']}/")
        if collection_name:
            db_databases = info_mongo()
            available = False
            for database in db_databases.keys():
                if collection_name in db_databases[database]["collections"]:
                    available = True
                    break
        else:
            available = True
    except requests.exceptions.ConnectionError:
        available = False
    return available


def db_client():
    # define data source
    return MongoClient(
        f'mongodb://{dave_settings()["db_user"]}:{dave_settings()["db_pw"]}@{dave_settings()["db_ip"]}',
        authSource="admin",
    )


def from_mongo(database, collection, filter_method=None, filter_param=None, filter_value=None):
    """
    This function requests data from the mongo db

    INPUT:
        **database** (string) - name of the database \n
        **collection** (string) - nome of the collection \n

    OPTIONAL:
        **filter_method** (string) - method for the data filtering. Examples: \n
        "eq" - matches documents where the value of a field equals the specified value. \n
        "geoIntersects" - Selects documents whose geospatial data intersects with a specified \
                geometrical object \n
        **filter_param** (string) - parameter to be filtered by \n
        **filter_value** (string) - value for the filtering
        
    """
    client = db_client()
    db = client[database]
    if all([filter_method is not None, filter_param is not None, filter_value is not None]):
        if filter_param == "geometry":
            # transform geometry from string to shapely object
            filter_value = loads(filter_value)
            # request data with geometrical filtering
            request = db[collection].find(
                {f"{filter_param}": {f"${filter_method}": {"$geometry": mapping(filter_value)}}}
            )
        else:
            # request data with filtering
            request = db[collection].find(
                {f"{filter_param}": {f"${filter_method}": f"{filter_value}"}}
            )
    else:
        # request all data from defined collection
        request = db[collection].find()
    data_list = list(request)
    if "geometry" in data_list[0].keys() and len(data_list) != 0:
        # convert geometries to shapely objects
        for row in data_list:
            if "geometry" in row.keys():
                row["geometry"] = shape(row["geometry"])
        if len(data_list) > 1:
            df = gpd.GeoDataFrame(data_list, crs=dave_settings()["crs_main"])
        elif len(data_list) == 1:
            df = gpd.GeoDataFrame([data_list[0]], crs=dave_settings()["crs_main"])
    elif len(data_list) != 0:
        if len(data_list) > 1:
            df = pd.DataFrame(data_list)
        elif len(data_list) == 1:
            df = pd.DataFrame([data_list[0]])
    else:
        df = pd.DataFrame([])
    # remove mongo db id object
    df.drop(columns=["_id"], inplace=True)
    return df


def df_to_mongo(database, collection, data_df):
    client = db_client()
    # request existing databases and list collections
    info = info_mongo()
    # check if collection is not None
    if collection and not db_availability(collection_name=collection):
        # check if database exist. No creation of new databases allowed
        if database in list(info.keys()):
            db = client[database]
            collection = db[collection]
            if isinstance(data_df, gpd.GeoDataFrame):
                # define that collection includes geometrical data
                collection.create_index([("geometry", GEOSPHERE)])
                # convert geometry to geojson
                data_df["geometry"] = data_df["geometry"].apply(lambda x: mapping(x))
            # convert df to dict
            data = data_df.to_dict(orient="records")
            # insert data to database
            if len(data) > 1:
                collection.insert_many(data)
            elif len(data) == 1:
                collection.insert_one(data[0])
        else:
            print(
                f"The choosen database is not existing. Please choose on of these: {list(info.keys())}"
            )
    else:
        print(
            f"Please rename collection because the name '{collection}' allready exists"
        ) if collection else print("Please set a collection name")


def df_to_mongo_merge(database, collection, data_df):
    """
    This function uploads data into the mongo db and merge it with an existing collection
    """
    client = db_client()
    # check if collection is not None
    if collection:
        # check if collection is available
        if db_availability(collection_name=collection):
            db = client[database]
            collection = db[collection]
            if isinstance(data_df, gpd.GeoDataFrame):
                # convert geometry to geojson
                data_df["geometry"] = data_df["geometry"].apply(lambda x: mapping(x))
            # convert df to dict
            data = data_df.to_dict(orient="records")
            # insert data to database
            if len(data) > 1:
                collection.insert_many(data)
            elif len(data) == 1:
                collection.insert_one(data[0])
        else:
            print(f"There is no collection with the name {collection} available to merge data")
    else:
        print("Please set a collection name")


def to_mongo(database, collection=None, data_df=None, filepath=None, merge=False):
    """
    This function uploads data into the mongo db. Hint: The choosen database has to exist

    INPUT:
        **database** (string) - name of the database where the data should added. Note: It is not
                                allowed to create a new database. Please use existing names or
                                contact the db admin
    OPTIONAL:
        **collection** (string) - name of the collection where the data should added. For DataFrames
                                  it is necessary
        **data_df** ((Geo)DataFrame) - the data which should uploaded as DataFrame or GeoDataFrame
        **filepath** (string) - absolute path to data if this is not in DataFrame format
        **merge** (boolean) - If True the uploaded data will be merged into an existing collection
    """
    # --- convert diffrent data formats
    # convert GeoDataFrame into DataFrame
    if data_df is not None:
        if merge:
            df_to_mongo_merge(database, collection, data_df)
        else:
            df_to_mongo(database, collection, data_df)
    elif filepath.split(".")[1] == "csv":
        pass
    elif filepath.split(".")[1] == "xlsx":
        pass
    elif filepath.split(".")[1] == "h5":
        # open hdf file
        file = pd.HDFStore(filepath)
        for key in file.keys():
            # rename collection in the case of multiple tables
            key_replaced = key.replace("/", "")
            if collection and len(file.keys()) > 1:
                # check if collection name is the same as the key start to avoid duplicates
                collection_new = (
                    key_replaced
                    if collection == key_replaced[: len(collection)]
                    else collection + f"_{key_replaced}"
                )
            elif collection:
                collection_new = collection
            else:
                # use key from hdf file
                collection_new = key_replaced
            # change spaces to underscores
            collection_new = collection_new.replace(" ", "_")
            # read data from file and convert geometry
            data = file.get(key)
            if "geometry" in data.keys() and isinstance(data.iloc[0].geometry, bytes):
                data = wkb_to_wkt(data, dave_settings()["crs_main"])
            # upload tables to mongo db
            df_to_mongo(database, collection_new, data)
        # close file
        file.close()


def create_database(database_names):
    """
    This function creates a new database in the DAVE database

    INPUT:
        **database_names** (list) - names of new databases which should create
    """
    client = db_client()
    for name in database_names:
        database = client[name]
        collection = database["init"]
        data = {"database_name": name, "description": f"This database staores {name} informations"}
        collection.insert_one(data)


def drop_collection(database, collection):
    """
    This function drops an existing collection from the database
    """
    client = db_client()
    db = client[database]
    # drop collection
    db[collection].drop()


def search_database(collection):
    """
    This function searches the suitable database name for a given collection name
    """
    db_info = info_mongo()
    database_name = None
    for database in db_info.keys():
        if collection in db_info[database]["collections"]:
            database_name = database
            break
    return database_name
