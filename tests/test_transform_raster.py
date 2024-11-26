import numpy as np
import rasterio
import os

from owslib.wms import WebMapService
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import os
import matplotlib.pyplot as plt
from shapely.geometry import box
import warnings
from rasterio.transform import from_bounds


def transform_image(input_path: object, output_path: object, crs: object, bbox: object) -> object:
    # Supress the warning of NotGeoreferencedWarning: Dataset has no geotransform, gcps, or rpcs. The identity matrix
    # will be returned. dataset = DatasetReader(path, driver=driver, sharing=sharing, **kwargs), as WMS result is an
    # image without geo-reference inherently.
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    _transform = from_bounds(*bbox, width=256, height=256)
    # Open the image and write it as a georeferenced raster
    with rasterio.open(input_path) as src:
        meta = src.meta.copy()
        meta.update({
            'driver': 'GTiff',
            'height': src.height,
            'width': src.width,
            'count': src.count,
            'crs': crs,
            'transform': _transform,
        })
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(src.read())
    return output_path


def test_transform_image():
    # Define test inputs
    input_path = 'test_input.tif'
    output_path = 'test_output.tif'
    crs = 'EPSG:4326'
    bbox = (0, 0, 10, 10)

    # Create a dummy input file for testing
    with rasterio.open(
        input_path, 'w',
        driver='GTiff', height=256, width=256,
        count=1, dtype='uint8') as dst:
        dst.write(np.ones((1, 256, 256), dtype='uint8'))

    # Run the function
    transform_image(input_path, output_path, crs, bbox)

    # Check the output file
    with rasterio.open(output_path) as src:
        assert src.crs == crs, "CRS does not match"
        assert src.transform == rasterio.transform.from_bounds(*bbox, width=256, height=256), "Transform does not match"
        assert src.width == 256 and src.height == 256, "Dimensions do not match"
        assert src.count == 1, "Band count does not match"

    # Clean up
    os.remove(input_path)
    os.remove(output_path)
    print("Test passed!")


# Execute the test
test_transform_image()
