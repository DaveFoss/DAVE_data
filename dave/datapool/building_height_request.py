import geopandas as gpd
import numpy as np
import rasterio
import tqdm
from owslib.wms import WebMapService
from shapely.geometry import Point

from dave.settings import dave_settings


# This fuction convert the raster to point
def raster_to_point(raster):
    with rasterio.open(raster) as src:
        data = src.read(1)  # Read the raster data
        transform = src.transform  # Get the transformation information

    # Get the coordinates and values of non-null pixels
    rows, cols = np.where(data != src.nodata)
    values = data[rows, cols]
    coords = [transform * (col, row) for row, col in zip(rows, cols)]

    # Create a GeoDataFrame with point geometries
    geometry = [Point(coord) for coord in coords]
    data = {"Value": values}
    gdf = gpd.GeoDataFrame(data, geometry=geometry, crs=src.crs)

    # In the raster file pixels with no building height is set to 65535. so we remove them fro mthe list of points
    condition = gdf["Value"] == 65535
    new_gdf = gdf[~condition]
    return new_gdf


# Request wms of building height from copernicus urban atlas
def request_building_height(grid_data, output_folder):
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create building heights:           ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # Create the counding box of the area of interest
    boundary = grid_data.area.geometry.unary_union
    boundary_bbox = boundary.bounds
    # update progress
    pbar.update(10)
    # WMS of building block height for the selected bounding box
    wms = WebMapService(
        "https://copernicus.discomap.eea.europa.eu/arcgis/services/UrbanAtlas/UA_BuildingHeights_2012_10m/ImageServer/WMSServer?request=GetCapabilities&service=WMS",
        version="1.1.1",
    )
    img = wms.getmap(
        layers=["0"],
        styles=["default"],
        srs="EPSG:4326",
        bbox=boundary_bbox,
        size=(300, 250),
        format="image/tiff",
        transparent=True,
    )
    # update progress
    pbar.update(40)
    # Save the building height in raster for the selected area of interest
    _selected_building_height = output_folder + "\\" + "building_height.tif"
    out = open(_selected_building_height, "wb")
    out.write(img.read())
    out.close()
    # update progress
    pbar.update(10)
    # Convert the raster to point and ssign the retrieved point to the result grid data
    grid_data.building_height = raster_to_point(_selected_building_height)
    # update progress
    pbar.update(40)
    # close progress bar
    pbar.close()
