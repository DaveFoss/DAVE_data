import contextily as cx
from matplotlib import pyplot as plt

from dave_data import osm_request

import geopandas as gpd
from tkinter.filedialog import askopenfile
fn = askopenfile(mode ='r', filetypes=[('Geo Files', '*.geojson')])
gdf = gpd.read_file(fn)

print(gdf.iloc[0].geometry)

streets = osm_request(
    "road",
    gdf.iloc[0].geometry,
)[0]
print(streets)
print(streets.crs)
streets_wm = streets.to_crs(epsg=3857)
ax = streets_wm.plot(figsize=(8, 8), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.DE)
ax.set_axis_off()
plt.show()
