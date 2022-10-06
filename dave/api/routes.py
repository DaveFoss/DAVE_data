# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

import geopandas as gpd
import pandas as pd
from fastapi import APIRouter, Depends, Request

from dave.api.request_bodys import Datapool_param, Dataset_param, Db_param, Db_up_param
from dave.create import create_grid
from dave.datapool.read_data import read_postal
from dave.io.database_io import from_mongo, info_mongo, to_mongo
from dave.io.file_io import to_json

router = APIRouter(
    prefix="",
)


# -------------------------------
#  System routes
# -------------------------------
# main page with root path information
@router.get("/")
def read_main(request: Request):
    return {"message": "Welcome to the DaVe API"}


# get method for database informations
@router.get("/db_info")
def db_info():
    return info_mongo()


# -------------------------------
#  DaVe routes
# -------------------------------
class DaveRequest:
    def create_dataset(self, parameters):
        # run DaVe main function to create a dataset
        grid_data = create_grid(
            postalcode=parameters.postalcode,
            town_name=parameters.town_name,
            federal_state=parameters.federal_state,
            nuts_region=parameters.nuts_regions,
            own_area=parameters.own_area,
            power_levels=parameters.power_levels,
            gas_levels=parameters.gas_levels,
            plot=parameters.plot,
            convert=parameters.convert,
            opt_model=parameters.opt_model,
            combine_areas=parameters.combine_areas,
            transformers=parameters.transformers,
            renewable_powerplants=parameters.renewable_powerplants,
            conventional_powerplants=parameters.conventional_powerplants,
            loads=parameters.loads,
            compressors=parameters.compressors,
            sources=parameters.sources,
            storages_gas=parameters.storages_gas,
        )
        # convert dave dataset to JSON string
        return to_json(grid_data)


# get method for dave dataset request
@router.get("/request_dataset")
def request_dataset(parameters: Dataset_param, dave: DaveRequest = Depends(DaveRequest)):
    grid_data = dave.create_dataset(parameters)
    return grid_data


# -------------------------------
#  Database routes
# -------------------------------
class DatapoolRequest:
    def get_postalcodes(self):
        # read postalcode area data from datapool
        postal, meta_data = read_postal()
        # convert postalcodes to JSON string
        postal_json = postal.postalcode.to_json()
        return postal_json

    def get_town_names(self):
        # read postalcode area data from datapool
        postal, meta_data = read_postal()
        # convert town_names to JSON string
        return postal.town.to_json()


# get method for datapool request
@router.get("/request_datapool")
def request_datapool(parameters: Datapool_param, pool: DatapoolRequest = Depends(DatapoolRequest)):
    if parameters.data_name == "postalcode":
        data = pool.get_postalcodes()
    elif parameters.data_name == "town_name":
        data = pool.get_town_names()
    # data = db.create_dataset()
    return data


class DbRequest:
    def db_request(self, parameters):
        # read data from mongo db
        data = from_mongo(
            database=parameters.database,
            collection=parameters.collection,
            filter_method=parameters.filter_method,
            geometry=parameters.geometry,
        )
        # convert postalcodes to JSON string
        return data.to_json()


# get method for database request
@router.get("/request_db")
def request_db(parameters: Db_param, db: DbRequest = Depends(DbRequest)):
    data = db.db_request(parameters)
    return data


class DbPost:
    def db_post(self, parameters):
        # convert string to geodataframe
        database = parameters.database
        collection = parameters.collection
        data = json.loads(parameters.data)
        # check if data from type geodataframe or dataframe
        if ("type" in data.keys()) and (data["type"] == "FeatureCollection"):
            data_df = gpd.GeoDataFrame.from_features(data)
        else:
            data_df = pd.DataFrame(data)
        # upload data into database
        to_mongo(database, collection, data_df)


# post method to upload data to database
@router.post("/post_db")
def post_db(parameters: Db_up_param, db: DbPost = Depends(DbPost)):
    db.db_post(parameters)
