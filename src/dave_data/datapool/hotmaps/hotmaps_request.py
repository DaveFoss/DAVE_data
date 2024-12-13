import os
import shutil
from pathlib import Path

import geopandas as gpd
import rasterio
import requests
from pyproj import CRS
from rasterio.features import shapes
from rasterio.mask import mask
from shapely import box
from shapely.geometry import shape

from dave_data.datapool.hotmaps.exception.hotmaps_exceptions import InvalidBbox
from dave_data.datapool.hotmaps.exception.hotmaps_exceptions import InvalidEPSG
from dave_data.datapool.hotmaps.exception.hotmaps_exceptions import OutOfBbox


def get_hotmaps_layer_info(layer_name):
    #     This function returns a dictionary with the information about hotmaps layers
    layer_info = {
        "Final energy demand density for space heating and domestic hot water - Total": {
            "title": "Final energy demand density for space heating and domestic hot water - Total",
            "tag": "heat_tot_curr_density",
            "key": "heat_tot_curr_density",
            "category": "heat",
        },
        "Final energy demand density for space heating and domestic hot water - Residential": {
            "title": "Final energy demand density for space heating and domestic hot water - Residential",
            "tag": "heat_res_curr_density",
            "key": "heat_res_curr_density",
            "category": "heat",
        },
        "Final energy demand density for space heating and domestic hot water - Non-Residential": {
            "title": "Final energy demand density for space heating and domestic hot water - Non-Residential",
            "tag": "heat_nonres_curr_density",
            "key": "heat_nonres_curr_density",
            "category": "heat",
        },
        "Space cooling needs density": {
            "title": "Space cooling needs density",
            "tag": "cool_tot_curr_density",
            "key": "cool_tot_curr_density",
            "category": "heat",
        },
        "Building gross floor area density - Residential": {
            "title": "Building gross floor area density - Residential",
            "tag": "gfa_res_curr_density",
            "key": "gfa_res_curr_density",
            "category": "",
        },
        "Building gross floor area density - Non-Residential": {
            "title": "Building gross floor area density - Non-Residential",
            "tag": "gfa_nonres_curr_density",
            "key": "gfa_nonres_curr_density",
            "category": "",
        },
        "Building gross floor area density - Total": {
            "title": "Building gross floor area density - Total",
            "tag": "gfa_tot_curr_density",
            "key": "gfa_tot_curr_density",
            "category": "",
        },
        "Building construction period - until 1975": {
            "title": "Building gross floor area density - Total",
            "tag": "ghs_built_1975_100_share",
            "key": "GHS_BUILT_1975_100_share",
            "category": "construction_periods",
        },
        "Population total": {
            "title": "Population total",
            "tag": "pop_tot_curr_density",
            "key": "pop_tot_curr_density",
            "category": "",
        },
        "Potential solar thermal collectors - rooftop": {
            "title": "Potential solar thermal collectors - rooftop",
            "tag": "potential_solarthermal_collectors_rooftop",
            "key": "potential_solarthermal_collectors_rooftop",
            "category": "potential",
        },
        "Potential solar thermal collectors - open field": {
            "title": "Potential solar thermal collectors - open field",
            "tag": "potential_solarthermal_collectors_open_field",
            "key": "potential_solarthermal_collectors_open_field",
            "category": "potential",
        },
    }

    # Check if the layer_name is valid
    if layer_name not in layer_info:
        # Prepare a message listing available layers
        available_layers = "\n".join(
            [f"{i + 1}. {layer}" for i, layer in enumerate(layer_info.keys())]
        )
        error_message = f"Layer '{layer_name}' not found. Available layers:\n{available_layers}"
        raise ValueError(error_message)

    # Return the information for the given type
    title = layer_info[layer_name]["title"]
    tag = layer_info[layer_name]["tag"]
    key = layer_info[layer_name]["key"]
    category = layer_info[layer_name]["category"]
    return title, tag, key, category


def validate_bbox(bbox):
    # Validate bbox
    if not (isinstance(bbox, (list, tuple)) and len(bbox) == 4):
        raise InvalidBbox(
            "bbox must be a list or tuple of four elements (min_lon, min_lat, max_lon, max_lat)."
        )
    if len(bbox) != 4:
        raise InvalidBbox(
            "Bounding box must have exactly four elements: [min_x, min_y, max_x, max_y]."
        )

    min_x, min_y, max_x, max_y = bbox

    if not (-180 <= min_x <= 180 and -180 <= max_x <= 180):
        raise InvalidBbox("Y values must be between -180 and 180 degrees.")

    if not (-90 <= min_y <= 90 and -90 <= max_y <= 90):
        raise InvalidBbox("X values must be between -90 and 90 degrees.")

    if max_x <= min_x:
        raise InvalidBbox("min_x should be less than max_x.")

    if max_y <= min_y:
        raise InvalidBbox("min_y should be less than max_y.")


def validate_epsg(epsg):
    # First, check if the EPSG code is an integer
    if not isinstance(epsg, int):
        raise InvalidEPSG("EPSG must be an integer.")

    try:
        # Attempt to create a CRS object with the EPSG code
        CRS.from_epsg(epsg)
    except Exception as e:
        print(f"EPSG code {epsg} is not valid: {e}")
        raise InvalidEPSG(f"EPSG code {epsg} is not valid: {e}") from e


def download_hotmaps_raster(title, tag, key, category, directory):
    # Gitlab link to request Hotmaps data
    url = f"https://gitlab.com/hotmaps//{category}/{tag}/raw/master/data/{key}.tif"
    response = requests.get(url, timeout=60)

    # The path to save the raster file
    raster_path = os.path.join(directory, title + ".tif")
    # Save the raster
    if response.status_code == 200:
        with Path.open(raster_path, "wb") as f:
            f.write(response.content)
    else:
        print("Failed to retrieve the image")
    return raster_path


def clip_raster(temp_directory, title, output_directory, bbox):
    # The path to save the saved raster file
    raster_path = os.path.join(temp_directory, title + ".tif")

    # Define the path to save the clipped raster file
    clipped_raster_path = os.path.join(output_directory, title + ".tif")

    # Prepare the bounding box to clip the raster
    _bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

    # Create a GeoDataFrame with the bounding box
    gdf = gpd.GeoDataFrame({"geometry": [_bbox]})

    # Set the original CRS (Coordinate Reference System)
    gdf.set_crs(epsg="4326", inplace=True)

    # Reproject to the new CRS - the CRS of the original HotMaps raster
    gdf = gdf.to_crs(epsg="3035")

    # Check if the raster_path is a string and the raster file exists
    if not isinstance(raster_path, str) or not Path(raster_path).exists():
        raise FileNotFoundError(
            f"Raster file '{raster_path}' does not exist or is not a valid path."
        )

    # Check if gdf is provided and has valid geometries
    if gdf is None or not hasattr(gdf, "geometry") or gdf.empty:
        raise ValueError(
            "GeoDataFrame 'gdf' is invalid or does not contain valid geometry."
        )

    # Check if clipped_raster_path is a string
    if not isinstance(clipped_raster_path, str):
        raise ValueError(
            f"Raster file '{clipped_raster_path}' is not a valid path."
        )

    # Load the GeoTIFF
    with rasterio.open(raster_path) as src:
        try:
            out_image, out_transform = mask(src, gdf.geometry, crop=True)
            out_meta = src.meta.copy()

            # Check if the out_image contains valid data
            if out_image is None or out_image.sum() == 0:
                print(
                    "The area does not fit within the clipping layer or is empty."
                )
                raise OutOfBbox(
                    "The area does not fit within the clipping layer or is empty."
                )

            # Update the metadata
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                }
            )
        except Exception as e:
            print(e.__class__.__name__)

    # Save the clipped GeoTIFF
    with rasterio.open(clipped_raster_path, "w", **out_meta) as dest:
        dest.write(out_image)
    return clipped_raster_path


def raster_to_vector(output_directory, title, epsg):
    # Define the path to save the clipped raster file
    clipped_raster_path = os.path.join(output_directory, title + ".tif")
    # Define the path to save the vector file in gpkg format
    vector_path = os.path.join(output_directory, title + ".gpkg")

    # Check if clipped_raster_path is a string and the file exists
    if (
        not isinstance(clipped_raster_path, str)
        or not Path(clipped_raster_path).exists()
    ):
        raise FileNotFoundError(
            f"Raster file '{clipped_raster_path}' does not exist or is not a valid path."
        )

    # Check if vector_path is a string
    if not isinstance(vector_path, str):
        raise ValueError(f"Vector path '{vector_path}' is not a valid string.")

    # Check if epsg is a valid integer
    if not isinstance(epsg, int):
        raise ValueError(f"EPSG code '{epsg}' is not a valid integer.")

    with rasterio.open(clipped_raster_path) as src:
        # Read the first band of the raster image
        image = src.read(1)
        # Create a mask for non-zero values
        mask = image != 0

        # Extracting the CRS from the raster
        raster_crs = src.crs
        raster_transform = src.transform

        # Generate shapes (polygons) from the raster
        results = (
            {"properties": {"value": value}, "geometry": geometry}
            for geometry, value in shapes(
                image, mask=mask, transform=raster_transform
            )
        )

        # Collect the features
        features = list(results)

        # Convert the extracted shapes to a GeoDataFrame
        geometries = [shape(feature["geometry"]) for feature in features]
        values = [feature["properties"]["value"] for feature in features]
        vector = gpd.GeoDataFrame(
            {"geometry": geometries, "value": values}, crs=raster_crs
        )
        # Reproject the vector to the EPSG of interest
        vector_proj = vector.to_crs(epsg=epsg)

        # Save the Geo-dataframe as a Geopackage
        vector_proj.to_file(vector_path, driver="GPKG")
        print(
            f"Vector file '{vector_path}' corresponding to the georeferenced raster file is "
            f"generated and added to the hotmaps_output folder."
        )
        return vector_path


def hotmaps_request(layer_name, bbox, epsg):
    # Validate layer_name
    if not isinstance(layer_name, str):
        raise ValueError("layer_name must be a string.")

    # Validate bbox
    validate_bbox(bbox)

    # Validate epsg
    validate_epsg(epsg)

    try:
        title = get_hotmaps_layer_info(layer_name)[0]
        tag = get_hotmaps_layer_info(layer_name)[1]
        key = get_hotmaps_layer_info(layer_name)[2]
        category = get_hotmaps_layer_info(layer_name)[3]
    except Exception as e:
        print(e)
        return

    # Create the temp and output directory if it doesn't exist
    output_directory = Path("hotmaps_output")
    temp_directory = Path("temp_output")

    output_directory.mkdir(parents=True, exist_ok=True)
    temp_directory.mkdir(parents=True, exist_ok=True)

    # Download HotMaps raster temporarily in the tep directory
    download_hotmaps_raster(title, tag, key, category, temp_directory)

    # Clip raster based on bounding box of interest
    clipped_raster = clip_raster(temp_directory, title, output_directory, bbox)

    # Convert clipped raster to vector
    vector = raster_to_vector(output_directory, title, epsg)

    # Remove temp directory and all its contents.
    try:
        shutil.rmtree(temp_directory)
        print(f"Directory '{temp_directory}' and all its contents removed.")
    except OSError as e:
        print(f"Error: {e}")

    return clipped_raster, vector
