import uvicorn
from fastapi import FastAPI

from dave.create import create_grid
from dave.api import request_bodys


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





# set a get
@app.get('/request_dataset')
def index():
    return request[-1]


# hand over parameters to DaVe
@app.post('/request_dataset')
def create_parameters(parameters: request_bodys.Dataset_param):
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