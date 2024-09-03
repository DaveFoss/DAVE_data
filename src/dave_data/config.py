"""
Project config reader.
Based on Steffen (https://github.com/steffenGit)

License: MIT
"""

__all__ = [
    "has_option",
    "has_section",
    "get",
    "get_list",
    "get_dict",
    "get_dict_list",
    "tmp_set",
    "init",
]

import configparser as cp
import logging
from pathlib import Path

BLACKLIST = ["tox.ini", "pytest.ini"]

cfg = cp.RawConfigParser()
cfg.optionxform = str
_loaded = False
FILES = []


def get_ini_filenames():
    """Returns a list of ini files to use."""
    paths = []

    package_path = Path(__file__).resolve().parent
    files = list(package_path.rglob("*.ini"))

    local_path = Path(Path.home(), ".dave")
    if local_path.is_dir():
        paths.append(local_path)
    logging.debug(f"Searching for .ini-files in the following paths {paths}")
    for p in paths:
        files.extend(list(p.glob("*.ini")))
    files = [f for f in files if f not in BLACKLIST]
    return files


def init(files=None):
    """Read config file(s).

    Parameters
    ----------
    files : list or None
        Absolute path to config file (incl. filename)
    """
    if files is None:
        files = get_ini_filenames()
    global FILES
    FILES = files
    cfg.read(files, encoding="utf-8")
    global _loaded
    _loaded = True


def load():
    if not _loaded:
        init()


def has_option(section, option):
    """Returns True if the given option exists in the given section."""
    return cfg.has_option(section, option)


def has_section(section):
    """Returns True if the given section exists."""
    return cfg.has_section(section)


def get(section, key):
    """Returns the value of a given key in a given section."""
    load()
    try:
        return cfg.getint(section, key)
    except ValueError:
        try:
            return cfg.getfloat(section, key)
        except ValueError:
            try:
                return cfg.getboolean(section, key)
            except ValueError:
                value = cfg.get(section, key)
                if value == "None":
                    value = None
                return value


def get_list(section, parameter, sep=",", string=False):
    """Returns the values (separated by sep) of a given key in a given
    section as a list.
    """
    try:
        my_list = get(section, parameter).split(sep)
        my_list = [x.strip() for x in my_list]

    except AttributeError:
        if string is True:
            my_list = list(cfg.get(section, parameter))
        else:
            my_list = list(get(section, parameter))
    return my_list


def get_dict(section):
    """Returns the values of a section as dictionary"""
    load()
    section_keys = dict(cfg.items(section)).keys()
    return {key: get(section, key) for key in section_keys}


def get_dict_list(section, string=False):
    """
    Returns the values of a section as dictionary. The values will be
    interpreted as list.
    """
    load()
    dc = {}
    for key, _value in cfg.items(section):
        dc[key] = get_list(section, key, string=string)
    return dc


def tmp_set(section, key, value):
    """
    Set/Overwrite a value temporarily for the actual section.
    """
    load()
    return cfg.set(section, key, value)


def get_base_path(sub_dir=None):
    if get("path", "base") is None:
        base_path = Path(Path.home(), "dave_data")
        tmp_set("path", "base", str(base_path))
    else:
        base_path = Path(get("path", "base"))
    if sub_dir is not None:
        allowed = get_list("path", "sub_dirs")
        if sub_dir in allowed:
            base_path = Path(base_path, sub_dir)
        else:
            raise ValueError(
                f"Subdir {sub_dir} is not valid. Use one of the following "
                f"subdirectories: {allowed}"
            )
    base_path.mkdir(exist_ok=True, parents=True)
    return base_path
