"""
Description: This module retrieve the streets from osm and plot them with the osm background.
License: MIT License.
"""

import contextily as cx
from matplotlib import pyplot as plt
from shapely import box

from dave_data.datapool.lod import lod

polygon = box(8.90, 53.16, 8.93, 53.15)
# polygon = box(13.40, 52.51, 13.41, 52.52)

lod_map = lod.get_lod(polygon)

lod_wm = lod_map.to_crs(epsg=3857)
ax = lod_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
plt.show()
