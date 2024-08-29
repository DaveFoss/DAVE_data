from collections import namedtuple
from dave_data.geometry.layers import get_federal_state_layer
import geopandas as gpd


def get_name_federal_state(polygon):
    poly = gpd.GeoDataFrame(index=[0], crs="epsg:4326", geometry=[polygon])
    Data = namedtuple("Data", "code name")
    fs_map = get_federal_state_layer()
    gdf = gpd.sjoin(fs_map, poly)
    if len(gdf) > 1:
        msg = (f"The give polygon touches more than one federal state.\n"
               f"This is not implemented so far.\n"
               f"Please divide your polygon, so that each polygon is within\n"
               f"just one fedral state.\n"
               f"The following states are touched by your polygon: "
               f"{gdf['name']}")
        raise NotImplementedError(msg)
    return Data(gdf["iso"].iloc[0], gdf["name"].iloc[0])
