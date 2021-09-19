import json

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point

# local url of the dave api
url = "http://141.5.108.4:8000"

# --- get DaVe database informations
request_info = requests.get(url + "/db_info")


# --- get data from DaVe database
# get full data of a collection (e.g. postalcodes)
request_a = requests.get(
    url + "/request_db", data=json.dumps({"database": "geodata", "collection": "postalcodes"})
)

# convert to data frame
data_a = gpd.GeoDataFrame.from_features(json.loads(request_a.json()))

# get postalcodes which intersects with a special geometrical point
point = Point(9.42035423449941, 51.23178804610007)

request_b = requests.get(
    url + "/request_db",
    data=json.dumps(
        {
            "database": "geodata",
            "collection": "postalcodes",
            "filter_method": "geoIntersects",
            "geometry": str(point),
        }
    ),
)
# convert to data frame
data_b = gpd.GeoDataFrame.from_features(json.loads(request_b.json()))


# --- upload data to DaVe database
d = {"col1": ["name1", "name2"], "geometry": [Point(1, 2), Point(2, 1)]}
gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
gdf_json = gdf.to_json()

r = requests.post(
    url + "/post_db",
    data=json.dumps({"database": "geodata", "collection": "upload_test", "data": gdf_json}),
)
