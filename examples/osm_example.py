import contextily as cx
from matplotlib import pyplot as plt
from shapely import box

from dave_data import osm_request

streets = osm_request(
    "road",
    box(13.40, 52.51, 13.41, 52.52),
)[0]
print(streets)
print(streets.crs)
streets_wm = streets.to_crs(epsg=3857)
ax = streets_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
plt.show()
