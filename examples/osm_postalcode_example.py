import contextily as cx
from matplotlib import pyplot as plt

from dave_data import osm_request
from dave_data import postalcode_to_polygon

# define area of interest by postalcode
polygon = postalcode_to_polygon(["34225"])
print(polygon)

# request streets for polygon
streets = osm_request("road", polygon)

# plot data
print(streets.meta.organisation)
streets_wm = streets.data.to_crs(epsg=3857)
ax = streets_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
plt.show()
