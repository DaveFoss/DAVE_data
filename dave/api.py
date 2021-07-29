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
def create_dataset():
    param = request[-1]
    grid_data = create_grid(postalcode=param['postalcode'],
                            town_name=param['town_name'],
                            federal_state=param['federal_state'],
                            nuts_region=param['nuts_regions'],
                            own_area=param['own_area'],
                            power_levels=param['power_levels'],
                            gas_levels=param['gas_levels'],
                            plot=param['plot'],
                            convert=param['convert'],
                            opt_model=param['opt_model'],
                            combine_areas=param['combine_areas'],
                            transformers=param['transformers'],
                            renewable_powerplants=param['renewable_powerplants'],
                            conventional_powerplants=param['conventional_powerplants'],
                            loads=param['loads'],
                            compressors=param['compressors'],
                            sources=param['sources'],
                            storages_gas=param['storages_gas'],
                            output_folder=param['output_folder'])
    return grid_data

# create request body
class Input(BaseModel):
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
@app.get('/api')
def index():
    return request[-1]

"""
# set a get
@app.get('/api')
def index():
    return create_dataset
"""


# hand over parameters to DaVe
@app.post('/api')
def create_parameters(parameters: Input):
    request.append(parameters)
    return request[-1]