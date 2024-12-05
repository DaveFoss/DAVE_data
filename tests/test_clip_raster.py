import os
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.mask import mask
import geopandas as gpd

from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import clip_raster


# Mocking rasterio.open
class MockRasterioDataset:
    def __init__(self, data):
        self.data = data
        self.meta = {
            'driver': 'GTiff',
            'count': 1,
            'dtype': 'uint8',
            'width': data.shape[2],
            'height': data.shape[1],
            'crs': 'EPSG:4326',
            'transform': from_origin(0, 10, 1, 1)  # Example transform
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self, band):
        return self.data


# Mocking the rasterio.open function
def mock_rasterio_open(filepath, mode='r'):
    # Create a dummy raster data (1 band, 5x5 pixels)
    dummy_data = np.array([[1, 1, 0, 0, 0],
                           [1, 1, 0, 0, 0],
                           [0, 0, 0, 0, 0],
                           [0, 0, 1, 1, 1],
                           [0, 0, 1, 1, 1]], dtype=np.uint8)  # Mock raster data
    return MockRasterioDataset(dummy_data)


# Mocking the mask function
def mock_mask(src, geometry, crop=True):
    # Simulate clipping by returning the original data and transform
    return src.read(1), src.meta['transform']


# Test function
def test_clip_raster():
    # Prepare test variables
    raster_path = 'path/to/mocked_raster.tif'  # Mocked input path
    clipped_raster_path = 'path/to/clipped_raster.tif'  # Output path
    os.makedirs(os.path.dirname(clipped_raster_path), exist_ok=True)  # Create directory for testing

    # Create a mock GeoDataFrame
    geometry = [  # Mocking a valid geometry
        {
            "type": "Polygon",
            "coordinates": [[(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)]]
        }
    ]
    gdf = gpd.GeoDataFrame({'geometry': geometry})

    # Mock rasterio and mask functions
    global rasterio
    original_rasterio_open = rasterio.open
    rasterio.open = mock_rasterio_open

    global mask
    original_mask = mask
    mask = mock_mask

    try:
        # Call the function
        result_path = clip_raster(raster_path, gdf, clipped_raster_path)

        # Verify the output path
        expected_path = clipped_raster_path
        assert result_path == expected_path, f"Test failed: Expected {expected_path} but got {result_path}."

        print(f"Test passed: Clipped raster would be saved to {result_path}")

    except FileNotFoundError as e:
        print(f"Test failed: {e}")
    except ValueError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # Clean up: Remove the test directory if it was created
        if os.path.exists(os.path.dirname(clipped_raster_path)):
            os.rmdir(os.path.dirname(clipped_raster_path))

        # Restore the original functions
        rasterio.open = original_rasterio_open
        mask = original_mask


# Call the test function
test_clip_raster()
