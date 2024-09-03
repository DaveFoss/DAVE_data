"""
Description: This module retrieve the streets from osm and plot them with the osm background.
License: MIT License.
"""

import pprint

import contextily as cx
from matplotlib import pyplot as plt
from shapely import box

from dave_data.datapool.osm import osm_request as osm

streets = osm.osm_request(
    "road",
    box(13.40, 52.51, 13.41, 52.52),
)
print(streets)
print(streets.data.crs)
pprint.pprint(streets.meta.__dict__)
streets_wm = streets.data.to_crs(epsg=3857)
ax = streets_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
plt.show()
