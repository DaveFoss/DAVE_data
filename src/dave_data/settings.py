from os import path
from pathlib import Path


def set_dave_data_settings():
    """
    This function returns a dictonary with the DAVE_data settings for used data and assumptions
    """
    settings = {
        # main definitions
        "dave_data_dir": Path(path.realpath(__file__)).parent,
        "dave_data_output_dir": Path(r"~\Desktop\DaVe_output").expanduser(),
        # structural definitions:
        "bar_format": "{desc:<10}{percentage:5.0f}%|{bar:30}| completed",  # format progress bar
        # geographical defintions:
        "crs_main": "EPSG:4326",  # crs which is based on the unit degree
        "crs_meter": "EPSG:3035",  # crs which is based on the unit meter
        # --- OSM data
        # osm time delay (because osm doesn't alowed more than 1 request per second)
        "osm_time_delay": 60,  # in seconds
        # osm tags: (type: (osm key, osm tags, osm type, parameter))
        "osm_tags": {
            "road": (
                "highway",
                [
                    "secondary",
                    "tertiary",
                    "unclassified",
                    "residential",
                    "living_street",
                    "footway",
                    "track",
                    "path",
                ],
                ["way"],
                ["geometry", "name", "highway", "surface"],
                "id",
            ),
            "landuse": (
                "landuse",
                True,
                ["way", "relation"],
                ["landuse", "geometry", "name", "id", "surface"],
            ),
            "leisure": (
                "leisure",
                ["golf_course", "garden", "park"],
                ["way", "relation"],
                [
                    "leisure",
                    "landuse",
                    "natural",
                    "name",
                    "geometry",
                    "id",
                    "surface",
                ],
            ),
            "natural": (
                "natural",
                ["scrub", "grassland", "water", "wood"],
                ["way", "relation"],
                [
                    "natural",
                    "landuse",
                    "leisure",
                    "name",
                    "geometry",
                    "id",
                    "surface",
                ],
            ),
            "building": (
                "building",
                True,
                ["way"],
                [
                    "addr:housenumber",
                    "addr:street",
                    "addr:suburb",
                    "amenity",
                    "building",
                    "building:levels",
                    "geometry",
                    "name",
                    "id",
                ],
            ),
            "railway": (
                "railway",
                [
                    "construction",
                    "disused",
                    "light_rail",
                    "monorail",
                    "narrow_gauge",
                    "rail",
                    "subway",
                    "tram",
                ],
                ["way"],
                [
                    "name",
                    "railway",
                    "geometry",
                    "tram",
                    "train",
                    "usage",
                    "voltage",
                    "id",
                ],
            ),
            "waterway": (
                "waterway",
                [
                    "river",
                    "stream",
                    "canal",
                    "tidal_channel ",
                    "pressurised",
                    "drain",
                ],
                ["way"],
                ["name", "waterway", "geometry", "depth", "width", "id"],
            ),
        },
        # osm categories
        "buildings_residential": [
            "apartments",
            "detached",
            "dormitory",
            "dwelling_house",
            "farm",
            "house",
            "houseboat",
            "residential",
            "semidetached_house",
            "static_caravan",
            "terrace",
            "yes",
        ],
        "buildings_commercial": [
            "commercial",
            "hall",
            "industrial",
            "kindergarten",
            "kiosk",
            "office",
            "retail",
            "school",
            "supermarket",
            "warehouse",
        ],
    }
    return settings


# load dave settings
dave_data_settings = set_dave_data_settings()
