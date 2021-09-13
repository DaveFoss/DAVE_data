import geopandas as gpd
import pandas as pd
from pymongo import GEOSPHERE, MongoClient
from shapely.geometry import mapping, shape
from shapely.wkt import loads

from dave.settings import dave_settings


def from_mongo(database, collection, filter_method=None, geometry=None):
    """
    This function requests data from the mongo db

    INPUT:
        **filter_method** (string) - method for the geometrical data filtering
        **geometry** (string) - shapely geometry object as string for the filtering
    """
    # define data source
    client = MongoClient(
        f'mongodb://{dave_settings()["db_user"]}:{dave_settings()["db_pw"]}@{dave_settings()["db_ip"]}'
    )
    db = client[database]
    if (filter_method is not None) and (geometry is not None):
        # transform geometry from string to shapely object
        geometry = loads(geometry)
        # request data with geometrical filtering
        request = db[collection].find(
            {"geometry": {f"${filter_method}": {"$geometry": mapping(geometry)}}}
        )
    else:
        # request all data from defined collection
        request = db[collection].find()
    data_list = list(request)
    # convert geometries to shapely objects
    for row in data_list:  #!!! add option for data with no geometry (convert to normal dataframe)
        row["geometry"] = shape(row["geometry"])
    if len(data_list) > 1:
        df = gpd.GeoDataFrame(data_list)
    elif len(data_list) == 1:
        df = gpd.GeoDataFrame([data_list[0]])
    else:
        df = pd.DataFrame([])
    # remove mongo db id object
    df.drop(columns=["_id"], inplace=True)
    return df


def to_mongo(database, collection, data_df):
    # define data source and create new database
    client = MongoClient(
        f'mongodb://{dave_settings()["db_user"]}:{dave_settings()["db_pw"]}@{dave_settings()["db_ip"]}'
    )
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
        collection.insert(data[0])
