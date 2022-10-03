# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import json

import geopandas as gpd
import pandas as pd
import request
import uvicorn
from fastapi import FastAPI

from dave.api import routes
from dave.datapool import read_postal
from dave.io import from_mongo, info_mongo, to_mongo

# initialize app object
app = FastAPI()

# include routes
app.include_router(routes.router)


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


# main page with root path information
@app.get("/")
def read_main(request: Request):
    return {"message": "Welcome to the DaVe API"}


# get method for dave dataset request
@app.get("/request_dataset")
def index(parameters: request_bodys.Dataset_param, dave: DaveRequest = Depends(DaveRequest)):
    grid_data = dave.create_dataset(parameters)
    return grid_data


# get method for datapool request
@app.get("/request_datapool")
def index_datapool(
    parameters: request_bodys.Datapool_param, pool: DatapoolRequest = Depends(DatapoolRequest)
):
    if parameters.data_name == "postalcode":
        data = pool.get_postalcodes()
    elif parameters.data_name == "town_name":
        data = pool.get_town_names()
    # data = db.create_dataset()
    return data


# get method for database request
@app.get("/request_db")
def index_db(parameters: request_bodys.Db_param, db: DbRequest = Depends(DbRequest)):
    data = db.db_request(parameters)
    return data


# post method to upload data to database
@app.post("/post_db")
def upload_db(parameters: request_bodys.Db_up_param, db: DbPost = Depends(DbPost)):
    db.db_post(parameters)


# get method for database informations
@app.get("/db_info")
def info_db():
    return info_mongo()


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=9000, reload=True)
