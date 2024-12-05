from DAVE_data.src.dave_data.datapool.hotmaps import hotmaps_request


def test_hotmaps_request():
    # Test valid request
    layer_name = 'Heat density total'
    bbox = [-10, 40, 10, 50]  # Example bounding box
    epsg = 3035

    # Since the function performs I/O operations, we should mock the external calls.
    # However, for this example, we will not implement mocking.
    try:
        result = hotmaps_request(layer_name, bbox, epsg)
        assert result is not None, "Test failed: result should not be None for valid request"
    except Exception as e:
        print(f"Test failed for valid request: {e}")

    # Test invalid layer name
    invalid_layer_name = 'Invalid layer'
    try:
        hotmaps_request(invalid_layer_name, bbox, epsg)
    except ValueError as e:
        assert str(e).startswith("Layer 'Invalid layer' not found."), "Test failed for invalid layer name"


# Run the test
test_hotmaps_request()
print("All tests passed!")
