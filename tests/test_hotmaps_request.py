from DAVE_data.src.dave_data.datapool.hotmaps import hotmaps_request


def test_hotmaps_request():
    # Test case setup
    layer_name = "Heat density total"
    bbox = (0, 45.08903556, 5.625, 48.92249926)

    # Call the function
    result = hotmaps_request(layer_name, bbox)

    # Assertions to verify expected outcomes
    if result is not None:
        assert not result.empty, "The result should not be empty"
        assert 'geometry' in result.columns, "Result should have a 'geometry' column"
        assert 'value' in result.columns, "Result should have a 'value' column"
        print("Test passed: Result is valid and contains the expected columns.")
    else:
        print("Test failed: No result returned.")


# Run the test
test_hotmaps_request()
