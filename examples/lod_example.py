"""
This module retrieve LoD1 data from Niedersachsen using a polygon.
License: MIT License.
"""

import pprint

import contextily as cx
from matplotlib import pyplot as plt
from shapely import box

from dave_data import osm_request
from dave_data.datapool.lod import lod

polygon = box(8.90, 53.16, 8.93, 53.15)
# polygon = box(13.40, 52.51, 13.41, 52.52)

lod = lod.get_lod(polygon)

pprint.pprint(lod.meta)

lod_map = lod.data

lod_wm = lod_map.to_crs(epsg=3857)
ax = lod_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
streets = osm_request(
    "road",
    polygon,
)
streets_wm = streets.data.to_crs(epsg=3857)
streets_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k", ax=ax)
plt.show()
