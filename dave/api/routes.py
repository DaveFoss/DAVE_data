# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

import geopandas as gpd
import pandapipes as ppi
import pandapower as pp
import pandas as pd
from fastapi import APIRouter, Depends, Request
from keycloak import KeycloakAuthenticationError, KeycloakOpenID

from dave.api.authentication import auth_token
from dave.api.request_bodys import (
    Auth_param,
    Datapool_param,
    Dataset_param,
    Db_create_database,
    Db_drop_col,
    Db_param,
    Db_up_param,
    Info_param,
    Update_param,
)
from dave.create import create_grid
from dave.datapool.db_update import update_database
from dave.datapool.read_data import read_postal
from dave.io.database_io import (
    create_database,
    db_availability,
    db_denied,
    drop_collection,
    from_mongo,
    info_mongo,
    to_mongo,
)
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
        if parameters.convert_power and parameters.convert_gas:
            # run DaVe main function to create a dataset
            grid_data, net_power, net_gas = create_grid(
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
                census=parameters.census,
            )
            # convert dave dataset to JSON string
            return json.dumps(
                {
                    "grid_data": to_json(grid_data),
                    "net_power": pp.to_json(net_power),
                    "net_gas": ppi.to_json(net_gas),
                }
            )
        elif parameters.convert_power:
            # run DaVe main function to create a dataset
            grid_data, net_power = create_grid(
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
                census=parameters.census,
            )
            # convert dave dataset to JSON string
            return json.dumps({"grid_data": to_json(grid_data), "net_power": pp.to_json(net_power)})
        elif parameters.convert_gas:
            # run DaVe main function to create a dataset
            grid_data, net_gas = create_grid(
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
                census=parameters.census,
            )
            # convert dave dataset to JSON string
            return json.dumps({"grid_data": to_json(grid_data), "net_gas": ppi.to_json(net_gas)})
        else:
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
                census=parameters.census,
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
    active, roles = auth_token(token=parameters.auth_token, roles=True)
    if active:
        return info_mongo(roles)
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
    def db_request(self, parameters, roles):
        # request database restrictions for the current user
        denied_databases, denied_collections = db_denied(roles)
        # read data from mongo db
        if parameters.database not in denied_databases:
            if parameters.collection not in denied_collections:
                if db_availability(collection_name=parameters.collection, roles=roles):
                    data = from_mongo(
                        database=parameters.database,
                        collection=parameters.collection,
                        filter_method=parameters.filter_method,
                        filter_param=parameters.filter_param,
                        filter_value=parameters.filter_value,
                    )
                    # convert data to JSON string
                    return data.to_json()
                else:
                    return "The requested collection is not available"
            else:
                return "You don't have access to this collection"
        else:
            return "You don't have access to this database"


# get method for database request
@router.get("/request_db")
def request_db(parameters: Db_param, db: DbRequest = Depends(DbRequest)):
    # authenticate user
    active, roles = auth_token(token=parameters.auth_token, roles=True)
    if active:
        data = db.db_request(parameters, roles)
        return data
    else:
        return "Token expired or invalid"


class DbPost:
    def db_post(self, parameters):
        # convert string to geodataframe
        data = json.loads(parameters.data)
        # check if data from type geodataframe or dataframe
        if ("type" in data.keys()) and (data["type"] == "FeatureCollection"):
            data_df = gpd.GeoDataFrame.from_features(data)
        else:
            data_df = pd.DataFrame(data)
        # upload data into database
        to_mongo(
            database=parameters.database,
            collection=parameters.collection,
            data_df=data_df,
            merge=parameters.merge,
        )


# post method to upload data to database
@router.post("/post_db")
def post_db(parameters: Db_up_param, db: DbPost = Depends(DbPost)):
    # authenticate user
    active_status, roles = auth_token(token=parameters.auth_token, roles=True)
    if active_status:
        if "developer" in roles:
            databases = info_mongo(roles).keys()
            if parameters.database in databases:
                db.db_post(parameters)
            else:
                return f"The choosen database is not existing. Please choose on of these: {list(databases)}"
        else:
            return "You need developer rights to upload data to the database"
    else:
        return "Token expired or invalid"


class Dbdrop:
    def db_drop(self, parameters):
        # drop collection from database
        database = parameters.database
        collection = parameters.collection
        drop_collection(database, collection)
        return f'The collection "{collection}" was successfully droped'


# get method to drop collection from database
@router.get("/drop_collection_db")
def drop_collection_db(parameters: Db_drop_col, drop: Dbdrop = Depends(Dbdrop)):
    # authenticate user
    active_status, roles = auth_token(token=parameters.auth_token, roles=True)
    if active_status:
        if "db_admin" in roles:
            return drop.db_drop(parameters)
        else:
            return "You need db_admin rights to drop a collections from database"
    else:
        return "Token expired or invalid"


class Dbcreate:
    def db_create(self, parameters):
        # create a database in db
        database_names = parameters.database_names
        create_database(database_names)
        return f'The database "{database_names}" was successfully created'


# get method to a databse in db
@router.get("/create_database_db")
def create_database_db(parameters: Db_create_database, create: Dbcreate = Depends(Dbcreate)):
    # authenticate user
    active_status, roles = auth_token(token=parameters.auth_token, roles=True)
    if active_status:
        if "db_admin" in roles:
            return create.db_create(parameters)
        else:
            return "You need db_admin rights to create a new database"
    else:
        return "Token expired or invalid"
