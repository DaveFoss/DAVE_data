# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

import geopandas as gpd
import pandas as pd
from fastapi import APIRouter, Depends, Request
from keycloak import KeycloakAuthenticationError, KeycloakOpenID

from dave.api.authentication import auth_token
from dave.api.request_bodys import (
    Auth_param,
    Datapool_param,
    Dataset_param,
    Db_param,
    Db_up_param,
    Info_param,
    Update_param,
)
from dave.create import create_grid
from dave.datapool.db_update import update_database
from dave.datapool.read_data import read_postal
from dave.io.database_io import db_availability, from_mongo, info_mongo, to_mongo
from dave.io.file_io import to_json
from dave.settings import dave_settings

router = APIRouter(
    prefix="",
)


# -------------------------------
#  System routes
# -------------------------------
# main page with root path information
@router.get("/")
def read_main(request: Request):
    return {"message": "Welcome to the DAVE API"}


# -------------------------------
#  Authentication
# -------------------------------
class Login:
    def request_token(self, parameters):
        # set keycloak open id client
        keycloak_openid = KeycloakOpenID(
            server_url=dave_settings()["keycloak_server_url"],
            client_id=dave_settings()["client_id"],
            realm_name=dave_settings()["realm_name"],
            client_secret_key=dave_settings()["client_secret_key"],
        )

        # request token from keycloak server
        try:
            token = keycloak_openid.token(parameters.user_name, parameters.user_password)
        except KeycloakAuthenticationError:
            token = "invalid user credentials"
        return token


# get method for login
@router.get("/login")
def login(parameters: Auth_param, auth: Login = Depends(Login)):
    token = auth.request_token(parameters)
    return token


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
            nuts_region=parameters.nuts_region,
            own_area=parameters.own_area,
            geodata=parameters.geodata,
            power_levels=parameters.power_levels,
            gas_levels=parameters.gas_levels,
            plot=parameters.plot,
            convert_power=parameters.convert_power,
            convert_gas=parameters.convert_gas,
            opt_model=parameters.opt_model,
            combine_areas=parameters.combine_areas,
            transformers=parameters.transformers,
            renewable_powerplants=parameters.renewable_powerplants,
            conventional_powerplants=parameters.conventional_powerplants,
            loads=parameters.loads,
            compressors=parameters.compressors,
            sinks=parameters.sinks,
            sources=parameters.sources,
            storages_gas=parameters.storages_gas,
            valves=parameters.valves,
        )
        # convert dave dataset to JSON string
        return to_json(grid_data)


# get method for dave dataset request
@router.get("/request_dataset")
def request_dataset(parameters: Dataset_param, dave: DaveRequest = Depends(DaveRequest)):
    # authenticate user
    if auth_token(token=parameters.auth_token):
        grid_data = dave.create_dataset(parameters)
        return grid_data
    else:
        return "Token expired or invalid"


# -------------------------------
#  Database routes
# -------------------------------
class DatapoolRequest:
    def get_postalcodes(self):
        # read postalcode area data from datapool
        postal, meta_data = read_postal()
        # convert postalcodes to JSON string
        return postal.postalcode.to_json()

    def get_town_names(self):
        # read postalcode area data from datapool
        postal, meta_data = read_postal()
        # convert town_names to JSON string
        return postal.town.to_json()


# get method for datapool request
@router.get("/request_datapool")  # !!! route rausnehmen da request db das auch funktioniert
def request_datapool(parameters: Datapool_param, pool: DatapoolRequest = Depends(DatapoolRequest)):
    # authenticate user
    if auth_token(token=parameters.auth_token):
        if parameters.data_name == "postalcode":
            data = pool.get_postalcodes()
        elif parameters.data_name == "town_name":
            data = pool.get_town_names()
        # data = db.create_dataset()
        return data
    else:
        return "Token expired or invalid"


# get method for database informations
@router.get("/db_info")
def db_info(parameters: Info_param):
    # authenticate user
    if auth_token(token=parameters.auth_token):
        return info_mongo()
    else:
        return "Token expired or invalid"


# get method for database update
@router.get("/db_update")
def db_update(parameters: Update_param):
    # authenticate user
    if auth_token(token=parameters.auth_token):
        update_database()
        return "Database successfully updated"
    else:
        return "Token expired or invalid"


class DbRequest:
    def db_request(self, parameters):
        # read data from mongo db
        if db_availability(collection_name=parameters.collection):
            data = from_mongo(
                database=parameters.database,
                collection=parameters.collection,
                filter_method=parameters.filter_method,
                filter_param=parameters.filter_param,
                filter_value=parameters.filter_value,
            )
            # convert postalcodes to JSON string
            return data.to_json()
        else:
            return "Database collection is not available"


# get method for database request
@router.get("/request_db")
def request_db(parameters: Db_param, db: DbRequest = Depends(DbRequest)):
    # authenticate user
    if auth_token(token=parameters.auth_token):
        data = db.db_request(parameters)
        return data
    else:
        return "Token expired or invalid"


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
    # authenticate user
    active_status, roles = auth_token(token=parameters.auth_token, roles=True)
    if active_status:
        if "developer" in roles:
            databases = info_mongo().keys()
            if parameters.database in databases:
                db.db_post(parameters)
            else:
                return f"The choosen database is not existing. Please choose on of these: {list(databases)}"
        else:
            return "You need developer rights to upload data to the database"
    else:
        return "Token expired or invalid"
