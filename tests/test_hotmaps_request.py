import pytest

from dave_data.datapool.hotmaps.exception.hotmaps_exceptions import InvalidBbox
from dave_data.datapool.hotmaps.exception.hotmaps_exceptions import InvalidEPSG
from dave_data.datapool.hotmaps.hotmaps_request import hotmaps_request


def test_valid_request():
    layer_name = "Final energy demand density for space heating and domestic hot water - Total"
    bbox = [
        14.348144531250002,
        51.7406361640977,
        14.3701171875,
        51.754240074033525,
    ]
    epsg = 4326

    try:
        clipped_raster, vector = hotmaps_request(layer_name, bbox, epsg)
        assert clipped_raster is not None, "clipped_raster should not be None"
        assert vector is not None, "vector should not be None"
    except Exception as e:
        pytest.raises(
            Exception, match=f"test_valid_request should not fail: {e}"
        )


def test_invalid_bbox():
    layer_name = "Final energy demand density for space heating and domestic hot water - Total"
    bbox = [0, 0, 0]  # Invalid bbox with only three coordinates
    epsg = 4326

    try:
        hotmaps_request(layer_name, bbox, epsg)
        pytest.raises(Exception, match="This should should not be valid")
    except InvalidBbox:
        assert True
    except Exception as e:
        pytest.raises(Exception, match=f"Something went wrong: {e}")


def test_invalid_layer_name():
    layer_name = "Invalid Layer Name"
    bbox = [
        14.348144531250002,
        51.7406361640977,
        14.3701171875,
        51.754240074033525,
    ]
    epsg = 4326

    try:
        hotmaps_request(layer_name, bbox, epsg)
        pytest.raises(
            Exception,
            match="test_invalid_layer_name failed: Exception expected",
        )
    except Exception:
        assert True


def test_invalid_epsg():
    layer_name = "Final energy demand density for space heating and domestic hot water - Total"
    bbox = [
        14.348144531250002,
        51.7406361640977,
        14.3701171875,
        51.754240074033525,
    ]
    epsg = 9999  # Assuming 9999 is not a valid EPSG code

    try:
        hotmaps_request(layer_name, bbox, epsg)
        pytest.raises(Exception, match="Should fail on invalid EPSG")
    except InvalidEPSG:
        assert True
    except Exception as e:
        pytest.raises(Exception, match=f"Something went wrong: {e}")
