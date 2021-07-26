from fastapi import FastAPI
from pydantic import BaseModel


# initialize app object
app = FastAPI()

# initialize voltage levels
request = []


# create request class
class Parameters(BaseModel):
    voltage_level: list


# set a get
@app.get('/')
def index():
    return request

# hand over parameters to DaVe
@app.post('/')
def create_parameters(parameters: Parameters):
    request.append(parameters)
    return request[-1]