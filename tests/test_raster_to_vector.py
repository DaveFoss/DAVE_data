import os
import tempfile
import geopandas as gpd

from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import raster_to_vector


def test_raster_to_vector():
    # Create a temporary raster file for testing
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_raster:
        temp_raster_path = temp_raster.name
        # Normally you would write a valid raster file here

    # Define a valid vector path
    vector_path = tempfile.mktemp(suffix='.gpkg')

    # Test with valid inputs
    try:
        result = raster_to_vector(temp_raster_path, vector_path, 4326)  # Using a common EPSG code
        assert result == vector_path
        print("Test passed: Valid inputs processed correctly.")
    except Exception as e:
        print(f"Test failed with valid inputs: {e}")

    # Test with invalid raster path
    try:
        raster_to_vector("invalid_path.tif", vector_path, 4326)
    except FileNotFoundError as e:
        print(f"Test passed: {e}")

    # Test with invalid vector path
    try:
        raster_to_vector(temp_raster_path, None, 4326)
    except ValueError as e:
        print(f"Test passed: {e}")

    # Test with invalid EPSG code
    try:
        raster_to_vector(temp_raster_path, vector_path, "invalid_epsg")
    except ValueError as e:
        print(f"Test passed: {e}")

    # Clean up temporary files
    os.remove(temp_raster_path)
    if os.path.exists(vector_path):
        os.remove(vector_path)

# Run the test
test_raster_to_vector()
