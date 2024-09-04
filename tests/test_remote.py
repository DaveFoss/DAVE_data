import os

from dave_data import config as cfg
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
