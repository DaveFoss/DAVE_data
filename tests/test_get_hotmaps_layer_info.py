from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import get_hotmaps_layer_info


def test_get_hotmaps_layer_info():
    # Test with a valid layer name
    result = get_hotmaps_layer_info('Heat density total')
    expected = (['heat_tot_curr_density'], 'Heat density total')
    assert result == expected, f"Expected {expected}, but got {result}"

    # Test with an invalid layer name
    result = get_hotmaps_layer_info('Invalid layer')
    assert 'error' in result, "Expected an error message, but didn't get one"
    assert result['error'].startswith("Layer 'Invalid layer' not found."), "Unexpected error message"

    # Test another valid layer name
    result = get_hotmaps_layer_info('Heat density residential sector')
    expected = (['heat_nonres_curr_density'], 'Heat density residential sector')
    assert result == expected, f"Expected {expected}, but got {result}"

    print("All tests passed!")


if __name__ == '__main__':
    test_get_hotmaps_layer_info()
