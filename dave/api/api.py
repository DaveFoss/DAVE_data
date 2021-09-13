import uvicorn
from fastapi import Depends, FastAPI

from dave.api import request_bodys
from dave.create import create_grid
from dave.datapool import read_postal
from dave.io import from_mongo, to_json

# initialize app object
app = FastAPI()


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


# get method for dave dataset request
@app.get("/request_dataset")
def index(parameters: request_bodys.Dataset_param, dave: DaveRequest = Depends(DaveRequest)):
    grid_data = dave.create_dataset(parameters)
    return grid_data


# get method for data from database request
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


# get method for data from database request
@app.get("/request_db")
def index_db(parameters: request_bodys.Db_param, db: DbRequest = Depends(DbRequest)):
    data = db.db_request(parameters)
    return data


"""
Außerdem noch zwei weitere Pfade (Endpunkte):
(Die beiden Punkte evt nur für Entwickler?)
/input_database: um Daten in die Datenbank zu schreiben
"""

"""
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
"""
