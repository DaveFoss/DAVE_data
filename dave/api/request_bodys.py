from pydantic import BaseModel
from typing import Optional

from dave import dave_output_dir


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
    output_folder: Optional[str] = dave_output_dir
