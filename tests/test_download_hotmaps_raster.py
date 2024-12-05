import os
import requests

from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import download_hotmaps_raster


def mock_requests_get(url):
    # Mocked response for a successful request
    class MockResponse:
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content

    # Check if the URL is correct
    if 'heat_tot_curr_density' in url:
        return MockResponse(200, b'This is dummy content for heat_tot_curr_density.tif')
    else:
        return MockResponse(404, b'Not found')


def test_download_hotmaps_raster():
    # Prepare test variables
    layer = 'heat_tot_curr_density'
    category = 'heat'
    directory = 'test_directory'  # Replace with a valid directory path if needed
    os.makedirs(directory, exist_ok=True)  # Create directory for testing

    # Mock the requests.get function
    original_requests_get = requests.get
    requests.get = mock_requests_get  # Replace the get function with the mock

    try:
        # Call the function
        raster_path = download_hotmaps_raster(layer, category, directory)

        # Verify the raster path
        expected_path = os.path.join(directory, layer + '.tif')

        # Check if the file was created
        assert os.path.exists(raster_path), f"Test failed: {raster_path} was not created."
        assert raster_path == expected_path, f"Test failed: Expected {expected_path} but got {raster_path}."

        print(f"Test passed: Raster downloaded and saved to {raster_path}")

    finally:
        # Clean up: Remove the test directory and files if they were created
        if os.path.exists(raster_path):
            os.remove(raster_path)
        os.rmdir(directory)

        # Restore the original requests.get function
        requests.get = original_requests_get


# Call the test function
test_download_hotmaps_raster()
