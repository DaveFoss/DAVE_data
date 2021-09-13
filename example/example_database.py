import json

import pandas as pd
import requests
from shapely.geometry import Point

# local url of the dave api
url = "http://127.0.0.1:8000"


# get full data of a collection (e.g. postalcodes)
request_a = requests.get(
    url + "/request_db", data=json.dumps({"database": "geodata", "collection": "postalcodes"})
)

# convert to data frame
data_a = pd.read_json(request_a.json(), orient="index")


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
data_b = pd.read_json(request_b.json(), orient="index")
