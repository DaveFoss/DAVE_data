__version__ = "v0.0.1"

from .core import compute
from .core import get_data
from .datapool.osm_request import osm_request
from .datapool.read_data import read_federal_states
from .datapool.read_data import read_nuts_regions
from .datapool.read_data import read_postal

__all__ = [
    "compute",
    "get_data",
    "osm_request",
    "read_postal",
    "read_federal_states",
    "read_nuts_regions",
]
