import os
import shutil
import requests
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely import box
from shapely.geometry import shape
from rasterio.features import shapes


def get_hotmaps_layer_info(layer_name):
    #     This function returns a dictionary with the information about hotmaps layers
    layer_info = {
        'Heat density total': {
            'title': 'Heat density total',
            'tag': 'heat_tot_curr_density',
            'category': 'heat'
        },
        'Heat density residential sector': {
            'title': 'Heat density residential sector',
            'tag': 'heat_res_curr_density',
            'category': 'heat'
        },
        'Heat density non-residential sector': {
            'title': 'Heat density non-residential sector',
            'tag': 'heat_nonres_curr_density',
            'category': 'heat'
        },
        'Cooling density total': {
            'title': 'Cooling density total',
            'tag': 'cool_tot_curr_density',
            'category': 'heat'
        },
        'Population total': {
            'title': 'Population total',
            'tag': 'pop_tot_curr_density',
            'category': ''
        },
        'Potential solar thermal collectors - roof top': {
            'title': 'Potential solar thermal collectors - roof top',
            'tag': 'potential_solarthermal_collectors_rooftop',
            'category': 'potential'
        },
        'Potential solar thermal collectors - open field': {
            'title': 'Potential solar thermal collectors - open field',
            'tag': 'potential_solarthermal_collectors_open_field',
            'category': 'potential'
        }
    }

    # Check if the layer_name is valid
    if layer_name not in layer_info:
        # Prepare a message listing available layers
        available_layers = "\n".join([f"{i + 1}. {layer}" for i, layer in enumerate(layer_info.keys())])
        error_message = f"Layer '{layer_name}' not found. Available layers:\n{available_layers}"
        raise ValueError(error_message)

    # Return the information for the given type
    tag = layer_info[layer_name]['tag']
    title = layer_info[layer_name]['title']
    category = layer_info[layer_name]['category']
    return [tag], title, category


def download_hotmaps_raster(layer, category, directory):
    # Gitlab link to request Hotmaps data
    url = f'https://gitlab.com/hotmaps//{category}/{layer}/raw/master/data/{layer}.tif'
    response = requests.get(url)

    # The path to save the raster file
    raster_path = os.path.join(directory, layer + '.tif')
    # Save the raster
    if response.status_code == 200:
        with open(raster_path, 'wb') as f:
            f.write(response.content)
    else:
        print('Failed to retrieve the image')
    return raster_path


def clip_raster(raster_path, gdf, clipped_raster_path):
    # Check if the raster_path is a string and the raster file exists
    if not isinstance(raster_path, str) or not os.path.exists(raster_path):
        raise FileNotFoundError(f"Raster file '{raster_path}' does not exist or is not a valid path.")

    # Check if gdf is provided and has valid geometries
    if gdf is None or not hasattr(gdf, 'geometry') or gdf.empty:
        raise ValueError("GeoDataFrame 'gdf' is invalid or does not contain valid geometry.")

    # Check if clipped_raster_path is a string
    if not isinstance(clipped_raster_path, str):
        raise ValueError(f"Clipped raster path '{clipped_raster_path}' is not a valid string.")

    # Load the GeoTIFF
    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, gdf.geometry, crop=True)
        out_meta = src.meta.copy()

        # Check if the out_image contains valid data
        if out_image is None or out_image.sum() == 0:
            print("The area does not fit within the clipping layer or is empty.")
            return None  # Return None or handle as needed

        # Update the metadata
        out_meta.update({
            'driver': 'GTiff',
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform
        })
    # Save the clipped GeoTIFF
    with rasterio.open(clipped_raster_path, 'w', **out_meta) as dest:
        dest.write(out_image)
    return clipped_raster_path


def raster_to_vector(clipped_raster_path, vector_path, epsg_code):
    # Check if clipped_raster_path is a string and the raster file exists
    if not isinstance(clipped_raster_path, str) or not os.path.exists(clipped_raster_path):
        raise FileNotFoundError(f"Raster file '{clipped_raster_path}' does not exist or is not a valid path.")

    # Check if vector_path is a string
    if not isinstance(vector_path, str):
        raise ValueError(f"Vector path '{vector_path}' is not a valid string.")

    # Check if epsg_code is a valid integer
    if not isinstance(epsg_code, int):
        raise ValueError(f"EPSG code '{epsg_code}' is not a valid integer.")

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
            {'properties': {'value': value}, 'geometry': geometry}
            for geometry, value in shapes(image, mask=mask, transform=raster_transform)
        )

        # Collect the features
        features = list(results)

        # Convert the extracted shapes to a GeoDataFrame
        geometries = [shape(feature['geometry']) for feature in features]
        values = [feature['properties']['value'] for feature in features]
        vector = gpd.GeoDataFrame({'geometry': geometries, 'value': values}, crs=raster_crs)
        # Reproject the vector to the EPSG of interest
        vector_proj = vector.to_crs(epsg=epsg_code)

        # Save the Geo-dataframe as a Geopackage
        vector_proj.to_file(vector_path, driver='GPKG')
        print(
            f"Vector file '{vector_path}' corresponding to the georeferenced raster file is "
            f"generated and added to the hotmaps_output folder.")
        return vector_path


def hotmaps_request(layer_name, bbox, epsg):
    # Validate layer_name
    if not isinstance(layer_name, str):
        raise ValueError("layer_name must be a string.")

    # Validate bbox
    if not (isinstance(bbox, (list, tuple)) and len(bbox) == 4):
        raise ValueError("bbox must be a list or tuple of four elements (min_lon, min_lat, max_lon, max_lat).")

    # Validate epsg
    if not isinstance(epsg, int):
        raise ValueError("epsg must be an integer.")
    try:
        layer = get_hotmaps_layer_info(layer_name)[0][0]
        category = get_hotmaps_layer_info(layer_name)[2]
    except Exception as e:
        print(e)
        return

    # Check if the layer is valid
    if 'error' in layer or not layer:
        print(f"Cannot process request: {layer.get('error', 'Invalid layer information')}")
        return

    # Create the temp and output directory if it doesn't exist
    output_directory = 'hotmaps_output'
    temp_directory = 'temp_output'
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(temp_directory, exist_ok=True)

    # Download HotMaps raster temporarily in the tep directory
    raster_path = download_hotmaps_raster(layer, category, temp_directory)

    # Prepare the bounding box to clip the raster
    _bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

    # Create a GeoDataFrame with the bounding box
    gdf = gpd.GeoDataFrame({'geometry': [_bbox]})

    # Set the original CRS (Coordinate Reference System)
    gdf.set_crs(epsg='4326', inplace=True)

    # Reproject to the new CRS - the CRS of the original HotMaps raster
    gdf = gdf.to_crs(epsg='3035')

    # Define the path to save the clipped raster file
    clipped_raster_path = os.path.join(output_directory, layer + '_clipped.tif')

    # Clip raster based on bounding box of interest
    clipped_raster_path = clip_raster(raster_path, gdf, clipped_raster_path)

    # Define the path to save the vector file in gpkg format
    vector_path = os.path.join(output_directory, layer + '.gpkg')
    # Convert clipped raster to vector
    vector = raster_to_vector(clipped_raster_path, vector_path, epsg)

    # Remove temp directory and all its contents.
    try:
        shutil.rmtree(temp_directory)
        print(f"Directory '{temp_directory}' and all its contents removed.")
    except OSError as e:
        print(f"Error: {e}")

    return vector
