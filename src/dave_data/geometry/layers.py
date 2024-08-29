from pathlib import Path

import geopandas as gpd

from dave_data import config as cfg
from dave_data.io.remote import download


def get_federal_state_layer():
    layer_path = Path(cfg.get_base_path("layer"))
    filename = cfg.get("file", "federal_states_layer")
    fn = Path(layer_path, filename)
    url = cfg.get("url", "owncloud") + filename
    download(fn, url)
    return gpd.read_file(fn)
