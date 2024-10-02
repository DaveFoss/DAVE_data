import logging
import os
from pathlib import Path

import requests

from dave_data import config as cfg


def set_proxy():
    proxy = f"{cfg.get('proxy', 'url')}:{cfg.get('proxy', 'port')}"
    os.environ["http_proxy"] = proxy
    os.environ["https_proxy"] = proxy


def remove_proxy():
    del os.environ["http_proxy"]
    del os.environ["https_proxy"]


def download(fn, url, force=False):
    """
    Download a file from a given url into a specific file if the file does not
    exist. Use `force=True` to force the download.

    Parameters
    ----------
    fn : Path or str
        Filename with the full path, where to store the downloaded file.
    url : str
        Full url of the file.
    force : bool
        Set to `True` to download the file even if it already exists.

    Examples
    --------
    >>> my_url = "https://upload.wikimedia.org/wikipedia/commons/d/d3/Test.pdf"
    >>> download("filename.pdf", my_url)
    >>> os.remove("filename.pdf")
    """
    fn = Path(fn)
    if cfg.get("proxy", "use_proxy") is True:
        set_proxy()
    if not fn.is_file() or force:
        logging.info("Downloading '%s' from %s", fn.name, url)
        try:
            req = requests.get(url, timeout=20)
        except requests.exceptions.ProxyError:
            remove_proxy()
            req = requests.get(url, timeout=20)

        with fn.open("wb") as fout:
            fout.write(req.content)
            logging.info("%s stored in %s.", fn.name, fn.parent)
    else:
        logging.debug("File '%s' exists. Download is skipped.", fn.name)
