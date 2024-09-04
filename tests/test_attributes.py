from shapely import box

from dave_data.geometry.attributes import divide_between_federal_states


def test_divide_between_federal_states():
    test_polygon = box(13.40, 52.51, 13.00, 52.30)
    poly = divide_between_federal_states(test_polygon)
    assert sorted(poly["name"]) == ["Berlin", "Brandenburg"]
