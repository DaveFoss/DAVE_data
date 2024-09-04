import os
from pathlib import Path

from dave_data import config as cfg
from dave_data.io.remote import download
from dave_data.io.remote import remove_proxy
from dave_data.io.remote import set_proxy


def test_proxy_switch():
    p_url = str(cfg.get("proxy", "url"))
    port = str(cfg.get("proxy", "port"))
    use = str(cfg.get("proxy", "use_proxy"))
    cfg.tmp_set("proxy", "url", "http://myprox.tester.de")
    cfg.tmp_set("proxy", "port", "76")
    set_proxy()
    assert os.environ.get("http_proxy") == "http://myprox.tester.de:76"
    remove_proxy()
    assert os.environ.get("http_proxy") is None
    cfg.tmp_set("proxy", "url", p_url)
    cfg.tmp_set("proxy", "port", port)
    cfg.tmp_set("proxy", "use_proxy", use)


def test_download_with_wrong_proxy():
    p_url = str(cfg.get("proxy", "url"))
    port = str(cfg.get("proxy", "port"))
    use = str(cfg.get("proxy", "use_proxy"))
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
    cfg.tmp_set("proxy", "url", p_url)
    cfg.tmp_set("proxy", "port", port)
    cfg.tmp_set("proxy", "use_proxy", use)
