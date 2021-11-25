import geopandas as gpd
import pandas as pd
from pymongo import GEOSPHERE, MongoClient
from shapely.geometry import mapping, shape
from shapely.wkt import loads

from dave.io.convert_format import wkb_to_wkt
from dave.settings import dave_settings


def db_client():
    # define data source
    return MongoClient(
        f'mongodb://{dave_settings()["db_user"]}:{dave_settings()["db_pw"]}@{dave_settings()["db_ip"]}'
    )


def info_mongo():
    info_mongo = {}
    client = db_client()
    # wirte databases
    for db in list(client.list_databases()):
        db_name = client[db["name"]]
        collections = []
        for collection in list(db_name.list_collections()):
            collections.append(collection["name"])
        db["collections"] = collections
        info_mongo[db["name"]] = db
    return info_mongo


def from_mongo(database, collection, filter_method=None, geometry=None):
    """
    This function requests data from the mongo db

    INPUT:
        **filter_method** (string) - method for the geometrical data filtering
        **geometry** (string) - shapely geometry object as string for the filtering
    """
    client = db_client()
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


def df_to_mongo(database, collection, data_df):
    client = db_client()
    # request existing databases
    info = info_mongo()
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
            collection.insert(data[0])
    else:
        print(
            f"The choosen database is not existing. Please choose on of these: {list(info.keys())}"
        )


def to_mongo(database, collection, data_df=None, filepath=None):
    """
    This function uploads data into the mongo db

    INPUT:
        **database** (string) - name of the database where the data should added. Note: It is not
                                allowed to create a new database. Please use existing names or
                                contact the db admin
        **collection** (string) - name of the collection where the data should added. If the given
                                  data has multiple tables (e.g.tabs in excel or hdf5 files) it
                                  would createt collections with the name <collection>_<key>
    OPTIONAL:
        **data_df** ((Geo)DataFrame) - the data which should uploaded as DataFrame or GeoDataFrame
        **filepath** (string) - absolute path to data if this is not in DataFrame format
    """
    # --- convert diffrent data formats
    # convert GeoDataFrame into DataFrame
    if data_df:
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
            if len(file.keys()) > 1:
                collection_new = collection + f"_{key.replace('/','')}"
            # read data from file and convert geometry
            data = file.get(key)
            if "geometry" in data.keys() and isinstance(data.iloc[0].geometry, bytes):
                data = wkb_to_wkt(data, dave_settings()["crs_main"])
            # upload tables to mongo db
            df_to_mongo(database, collection_new, data)
        # close file
        file.close()
