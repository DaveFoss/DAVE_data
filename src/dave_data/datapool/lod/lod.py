from pathlib import Path

import geopandas as gpd
import pandas as pd

from dave_data import config as cfg
from dave_data.core import Data
from dave_data.core import MetaData
from dave_data.geometry import attributes as da
from dave_data.io import remote


def get_lod_path(polygon=None, code=None):
    lod_path = Path(cfg.get_base_path(), "lod")
    if code is None:
        code = da.get_name_federal_state(polygon).code
    fs_path = Path(lod_path, code)
    fs_path.mkdir(exist_ok=True, parents=True)
    return fs_path


def get_file_map(polygon, n_lod=1):
    fs = da.get_name_federal_state(polygon)
    url = cfg.get(f"url lod{n_lod}", fs.code)
    file = url.split("/")[-1]
    fs_path = get_lod_path(code=fs.code)
    fn = Path(fs_path, file)
    remote.download(fn, url)
    return gpd.read_file(fn)


def get_url_list(polygon, n_lod=1, column="zip"):
    gdf = gpd.GeoDataFrame(index=[0], crs="epsg:4326", geometry=[polygon])
    file_map = get_file_map(polygon, n_lod)
    return gpd.sjoin(file_map, gdf)[column]


def get_lod(polygon, n_lod=1):
    tiles = {}
    polygon_parts = da.divide_between_federal_states(polygon)

    fs = da.get_name_federal_state(polygon)
    meta = MetaData(
        source_license=cfg.get(fs.code, "license"),
        organisation=cfg.get(fs.code, "organisation"),
        source_url=cfg.get(fs.code, "url"),
    )
    data = Data(
        name=f"LoD{n_lod}",
        description=f"LoD{n_lod}, {fs.name}",
        polygon=polygon,
        tags=cfg.get_list(f"lod{n_lod}", "tags"),
        meta=meta,
    )
    for url in get_url_list(polygon, n_lod):
        file = url.split("/")[-1]
        lod_path = get_lod_path(polygon=polygon)
        fn = Path(lod_path, file)
        remote.download(fn, url)
        tiles[file] = gpd.read_file(fn, engine="fiona")

    data.data = gpd.GeoDataFrame(pd.concat(tiles.values(), ignore_index=True))
    return data


def lod2gdb(polygon, fn, n_lod=1):
    lod = get_lod(polygon, n_lod)
    lod.to_file(fn)
