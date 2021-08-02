import uvicorn
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

from dave import dave_output_dir
from dave.create import create_grid


# initialize app object
app = FastAPI()

# initialize voltage levels
request = [] # muss nach request nur wieder gelöscht werden
# daraus noch ein dict machen


# run DaVe main function
def create_dataset(parameters):
    #param = request[-1]
    grid_data = create_grid(postalcode=parameters['postalcode'],
                            town_name=parameters['town_name'],
                            federal_state=parameters['federal_state'],
                            nuts_region=parameters['nuts_regions'],
                            own_area=parameters['own_area'],
                            power_levels=parameters['power_levels'],
                            gas_levels=parameters['gas_levels'],
                            plot=parameters['plot'],
                            convert=parameters['convert'],
                            opt_model=parameters['opt_model'],
                            combine_areas=parameters['combine_areas'],
                            transformers=parameters['transformers'],
                            renewable_powerplants=parameters['renewable_powerplants'],
                            conventional_powerplants=parameters['conventional_powerplants'],
                            loads=parameters['loads'],
                            compressors=parameters['compressors'],
                            sources=parameters['sources'],
                            storages_gas=parameters['storages_gas'],
                            output_folder=parameters['output_folder'])
    return request[-1]


# create request body for the DaVe dataset request
class Dataset_param(BaseModel):
    # these are all parameters needed in the dave main function
    postalcode: Optional[list] = None
    town_name: Optional[list] = None
    federal_state: Optional[list] = None
    nuts_regions: Optional[list] = None
    own_area: Optional[str] = None
    power_levels: Optional[list] = []
    gas_levels: Optional[list] = []
    plot: Optional[bool] = True
    convert: Optional[bool] = True
    opt_model: Optional[bool] = True
    combine_areas: Optional[list] = []
    transformers: Optional[bool] = True
    renewable_powerplants: Optional[bool] = True
    conventional_powerplants: Optional[bool] = True
    loads: Optional[bool] = True
    compressors: Optional[bool] = True
    sources: Optional[bool] = True
    storages_gas: Optional[bool] = True
    outputfolder: Optional[str] = dave_output_dir


# set a get
@app.get('/request_dataset')
def index():
    return request[-1]


# hand over parameters to DaVe
@app.post('/request_dataset')
def create_parameters(parameters: Dataset_param):
    # request.append(parameters)
    # return request[-1]
    # create_dataset(parameters)
    return parameters


"""
# set a get
@app.get('/api')
def create(postalcode: list[], test: str):
    plz={'test': test}
    return plz
"""


"""
Außerdem noch zwei weitere Pfade (Endpunkte):
(Die beiden Punkte evt nur für Entwickler?)
/input_database: um Daten in die Datenbank zu schreiben
/request_database: um rohdaten aus der DB zu holen
"""

"""
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
"""