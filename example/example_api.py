import json

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import Point

# local url of the dave api
# url = "http://141.5.108.4:8000"  # production server
url = "http://127.0.0.1:80/api"  # develop local

# --- get DaVe database informations
"""
With this script you can get the main informations from the dave database 
This includes all mongo db databases and their collections
"""
request_info = requests.get(url + "/db_info")
db_info = request_info.json()
data_a = gpd.GeoDataFrame.from_features(json.loads(request_info.json()))

# --- get data from DaVe database
# get full data of a collection (e.g. postalcodes)
"""
With this script you can download all data from collection for a database
"""
database_name = "geodata"
collection_name = "postalcodes"
request_collection = requests.get(
    url + "/request_db", data=json.dumps({"database": database_name, "collection": collection_name})
)
data_collection = gpd.GeoDataFrame.from_features(json.loads(request_collection.json()))

# get filtert part of a collection
"""
With this script you can download a geometrical filtert part of a collection
Example: All postalcodes which intersects with a special geometrical point
"""
point = Point(9.42035423449941, 51.23178804610007)
request_geo = requests.get(
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
data_geo = gpd.GeoDataFrame.from_features(json.loads(request_geo.json()))


# --- upload data to DaVe database
"""
With this script you can upload data to the database
Example: Add points to a new/existing collection at an new/existing database
"""
d = {"col1": ["name1", "name2"], "geometry": [Point(1, 2), Point(2, 1)]}
gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
gdf_json = gdf.to_json()

r = requests.post(
    url + "/post_db",
    data=json.dumps({"database": "geodata_test", "collection": "upload_test2", "data": gdf_json}),
)
