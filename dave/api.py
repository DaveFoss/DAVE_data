from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel


# initialize app object
app = FastAPI()

# initialize voltage levels
request = [] # muss nach request nur wieder gelöscht werden
# daraus noch ein dict machen


# create request body
class Input(BaseModel):
    postalcode: Optional[list] = None
    # town_name: list
    # federal_state: list
    # nuts_regions: list
    voltage_level: list
    gas_level: list


# set a get
@app.get('/api')
def index():
    return request[0]

# hand over parameters to DaVe
@app.post('/api')
def create_parameters(parameters: Input):
    request.append(parameters)
    return request[-1]