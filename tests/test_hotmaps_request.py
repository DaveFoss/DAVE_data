from dave_data.datapool.hotmaps.hotmaps_request import hotmaps_request


def test_hotmaps_request():
    # Test valid request
    layer_name = 'Heat density total'
    bbox = [14.348144531250002, 51.7406361640977, 14.3701171875, 51.754240074033525]  # Example bounding box
    epsg = 4326

    # Since the function performs I/O operations, we should mock the external calls.
    # However, for this example, we will not implement mocking.
    try:
        result = hotmaps_request(layer_name, bbox, epsg)
        assert result is not None, "Test failed: result should not be None for valid request"
    except Exception as e:
        print(f"Test failed for valid request: {e}")
        assert False, "Test failed with exception"

    # Test invalid layer name
    invalid_layer_name = 'Invalid layer'
    try:
        result = hotmaps_request(invalid_layer_name, bbox, epsg)
        assert result is None, "Test failed: result should be None for invalid request"

    except ValueError as e:
        assert True
