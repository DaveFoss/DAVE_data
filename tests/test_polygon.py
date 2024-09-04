from pathlib import Path

from shapely.geometry import Polygon

import dave_data.config as cfg
from dave_data.geometry.polygon import file_to_polygon
from dave_data.io.remote import download


def test_file_to_polygon():
    filename = "hertingshausen_test_dpo9z.geojson"
    file = Path(cfg.get_base_path(), filename)
    url = cfg.get("url", "owncloud") + filename
    file.unlink(missing_ok=True)
    download(file, url)
    polygon_file = file_to_polygon(file)
    assert isinstance(polygon_file, Polygon)
    file.unlink()
