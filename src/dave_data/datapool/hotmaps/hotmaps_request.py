import shutil
from owslib.wms import WebMapService
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import os
from shapely.geometry import box
import warnings
from rasterio.transform import from_bounds


def get_hotmaps_layer_info(layer_name):
    #     This function returns a dictionary with the information about hotmaps layers
    layer_info = {
        'Heat density total': {
            'title': 'Heat density total',
            'tag': 'heat_tot_curr_density'
        },
        'Heat density residential sector': {
            'title': 'Heat density residential sector',
            'tag': 'heat_nonres_curr_density'
        },
        'Heat density non-residential sector': {
            'title': 'Heat density non-residential sector',
            'tag': 'heat_nonres_curr_density'
        },
        'Cooling density total': {
            'title': 'Cooling density total',
            'tag': 'cool_tot_curr_density'
        },
        'Population total': {
            'title': 'Population total',
            'tag': 'pop_tot_curr_density'
        },
        'Potential solar thermal collectors - roof top': {
            'title': 'Potential solar thermal collectors - roof top',
            'tag': 'potential_solarthermal_collectors_rooftop'
        },
        'Potential solar thermal collectors - open field': {
            'title': 'Potential solar thermal collectors - open field',
            'tag': 'potential_solarthermal_collectors_open_field'
        }
    }
    # Check if information for the type was found
    if layer_name not in layer_info:
        # Prepare a message listing available layers
        available_layers = "\n".join([f"{i + 1}. {layer}" for i, layer in enumerate(layer_info.keys())])
        error_message = f"Layer '{layer_name}' not found. Available layers:\n{available_layers}"
        return {'error': error_message}

    else:
        # Return the information for the given type
        tag = layer_info.get(layer_name, {}).get('tag', '')
        title = layer_info.get(layer_name, {}).get('title', '')
        return [tag], title


def hotmaps_request(layer_name, bbox):
    """
    This function requests HotMaps data directly from HotMaps WebMapService (WMS)

    Examples
    --------
    # >>> heat_density_total = hotmaps_request("Heat density total",
    # >>> (0, 45.08903556, 5.625, 48.92249926))
    True

    """
    # Prepare the bounding box (bbox) information to be used in HotMaps WMS request.
    # Create a shapely box (polygon) from the bbox
    bbox_polygon = box(bbox[0], bbox[1], bbox[2], bbox[3])

    # Create a GeoDataFrame with this box and set the CRS to 4326
    bbox_gdf = gpd.GeoDataFrame({'geometry': [bbox_polygon]}, crs="EPSG:4326")
    # Convert the GeoDataFrame to CRS 3857
    bbox_3857_polygon = bbox_gdf.to_crs("EPSG:3857")
    # Extract the transformed bbox using total_bounds
    bbox_3857 = tuple(float(x) for x in bbox_3857_polygon.total_bounds)

    # Prepare the layer information to be used in HotMaps WMS request
    layer = get_hotmaps_layer_info(layer_name)

    # Check if the layer is valid
    if 'error' in layer or not layer:
        print(f"Cannot process request: {layer.get('error', 'Invalid layer information')}")
        return

    # Define the temporary directory and file path
    directory = "temp"
    original_file_name = "temp.tif"
    georeferenced_file_name = "temp_proj.tif"
    original_file_path = os.path.join(directory, original_file_name)
    georeferenced_file_path = os.path.join(directory, georeferenced_file_name)
    print("Temporary directory 'temp' is generated and raster file retrieved from the WMS is added to the folder.")

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    url = 'https://geoserver.hotmaps.eu/geoserver/hotmaps/wms?service=WMS'
    wms = WebMapService(url)
    img = wms.getmap(layers=layer[0],
                     crs='EPSG:3857',
                     version='1.3.0',
                     bbox=bbox_3857,
                     size=(300, 250),
                     format='image/png',
                     srs='EPSG:4326',
                     transparent=True
                     )
    out = open(original_file_path, 'wb')
    out.write(img.read())
    out.close()

    add_georeferencing(original_file_path, georeferenced_file_path, "EPSG: 4326", bbox)
    vector = raster_to_shape(georeferenced_file_path, layer[1])

    # Remove the directory and all its contents
    try:
        shutil.rmtree(directory)
        print(f"Directory '{directory}' and all its contents removed.")
    except OSError as e:
        print(f"Error: {e}")

    return vector


def add_georeferencing(input_file, output_file, crs, bbox):
    # Supress the warning of NotGeoreferencedWarning: Dataset has no geotransform, gcps, or rpcs. The identity matrix
    # will be returned. dataset = DatasetReader(path, driver=driver, sharing=sharing, **kwargs), as WMS result is an
    # image without geo-reference inherently.
    # This function is providing georeferencing for the raster file.
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    transform = from_bounds(*bbox, width=256, height=256)
    with rasterio.open(input_file) as src:
        data = src.read()
        profile = src.profile
    # Update the profile with the new CRS and transform
    profile.update({
        'crs': crs,
        'transform': transform
    })

    # Write the data to a new file with georeferencing
    try:
        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(data)
            print("The retrieved raster file is georeferenced and added to the 'temp' directory.")
    except Exception as e:
        print(f"Error writing output file: {e}")
    return output_file


def raster_to_shape(raster, layer_name):
    with rasterio.open(raster) as src:
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
        layer_path = layer_name + '.gpkg'
        # Save the Geo-dataframe as a Geopackage
        vector.to_file(layer_path, driver='GPKG')
        print(
            f"Vector file '{layer_path}' corresponding to the georeferenced raster file is generated and added to the root folder.")

    return vector
