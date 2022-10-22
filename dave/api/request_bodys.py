# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from typing import Optional

from pydantic import BaseModel

from dave.settings import dave_settings


# create authentification body for the login
class Auth_param(BaseModel):
    user_name: str
    user_password: str


# create request body for the DaVe dataset request
class Dataset_param(BaseModel):
    # these are all parameters needed in the dave main function
    postalcode: Optional[list] = None
    town_name: Optional[list] = None
    federal_state: Optional[list] = None
    nuts_regions: Optional[list] = None
    own_area: Optional[str] = None
    roads: Optional[bool] = False
    roads_plot: Optional[bool] = False
    buildings: Optional[bool] = False
    landuse: Optional[bool] = False
    railways: Optional[bool] = False
    power_levels: Optional[list] = []
    gas_levels: Optional[list] = []
    plot: Optional[bool] = True
    convert_power: Optional[list] = []
    convert_gas: Optional[list] = []
    opt_model: Optional[bool] = True
    combine_areas: Optional[list] = []
    transformers: Optional[bool] = True
    renewable_powerplants: Optional[bool] = True
    conventional_powerplants: Optional[bool] = True
    loads: Optional[bool] = True
    compressors: Optional[bool] = True
    sinks: Optional[bool] = True
    sources: Optional[bool] = True
    storages_gas: Optional[bool] = True
    valves: Optional[bool] = True
    output_folder: Optional[str] = dave_settings()["dave_output_dir"]


# create request body for the datapool request
class Datapool_param(BaseModel):
    data_name: str


# create request body for the database request
class Db_param(BaseModel):
    database: str
    collection: str
    filter_method: Optional[str] = None
    filter_param: Optional[str] = None
    filter_value: Optional[str] = None


# create request body for upload to the database
class Db_up_param(BaseModel):
    database: str
    collection: str
    data: str
    # meta_data ?
