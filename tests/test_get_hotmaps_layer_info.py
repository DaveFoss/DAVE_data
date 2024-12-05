from dave_data.datapool.hotmaps.hotmaps_request import get_hotmaps_layer_info


def test_get_hotmaps_layer_info():
    # Test cases
    try:
        # Test existing layer
        tag, title, category = get_hotmaps_layer_info('Heat density total')
        assert tag == ['heat_tot_curr_density'], "Test failed: Incorrect tag for 'Heat density total'"
        assert title == 'Heat density total', "Test failed: Incorrect title for 'Heat density total'"
        assert category == 'heat', "Test failed: Incorrect category for 'Heat density total'"
        print("Test passed: 'Heat density total'")

        # Test non-existing layer
        try:
            get_hotmaps_layer_info('Non-existent layer')
        except ValueError as e:
            assert str(e).startswith(
                "Layer 'Non-existent layer' not found"), "Test failed: Incorrect error message for non-existent layer"
            print("Test passed: 'Non-existent layer'")

        # Test another existing layer
        tag, title, category = get_hotmaps_layer_info('Potential solar thermal collectors - roof top')
        assert tag == [
            'potential_solarthermal_collectors_rooftop'], "Test failed: Incorrect tag for 'Potential solar thermal collectors - roof top'"
        assert title == 'Potential solar thermal collectors - roof top', "Test failed: Incorrect title for 'Potential solar thermal collectors - roof top'"
        assert category == 'potential', "Test failed: Incorrect category for 'Potential solar thermal collectors - roof top'"
        print("Test passed: 'Potential solar thermal collectors - roof top'")

    except AssertionError as e:
        print(e)


