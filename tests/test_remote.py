import os
from pathlib import Path

from dave_data import config as cfg
from dave_data.io.remote import download
from dave_data.io.remote import remove_proxy
from dave_data.io.remote import set_proxy


def test_proxy_switch():
    cfg.tmp_set("proxy", "url", "http://myprox.tester.de")
    cfg.tmp_set("proxy", "port", "76")
    assert os.environ.get("http_proxy") is None
    set_proxy()
    assert os.environ.get("http_proxy") == "http://myprox.tester.de:76"
    remove_proxy()
    assert os.environ.get("http_proxy") is None


def test_download_with_wrong_proxy():
    cfg.tmp_set("proxy", "url", "http://myprox.tester.de")
    cfg.tmp_set("proxy", "port", "76")
    cfg.tmp_set("proxy", "use_proxy", "True")
    filename = "hertingshausen_test_dpo9z.geojson"
    file = Path(cfg.get_base_path(), filename)
    file.unlink(missing_ok=True)
    url = cfg.get("url", "owncloud") + filename
    download(file, url)
    assert file.is_file()
    download(file, url)
    assert file.is_file()
    file.unlink()
    assert ~file.is_file()
