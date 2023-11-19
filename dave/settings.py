# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import os

# --- switch develop stage
# develop mode: running dave from ide and keycloak in local docker network
# local mode: runing dave and keycloak in local docker network
# production mode: running dave and keycloak on production server docker network
stage = "production"  # set development modus
if stage == "develop":
    # --- parameter for develop mode
    # keycloak settings
    keycloak_server_url = "http://127.0.0.1/auth/"
    client_secret_key = "3c5930ec-e5fc-43cb-a3f2-cdeb0811c404"
    # mongo db url
    db_url = "127.0.0.1:27017"
elif stage == "local":
    # --- parameter for local porduction mode
    # keycloak settings
    keycloak_server_url = "http://172.20.0.3/auth/"  # traefik ip because kecloak is set PROXY_ADRESS_FORWARDING = True
    client_secret_key = "3c5930ec-e5fc-43cb-a3f2-cdeb0811c404"
    # mongo db url
    db_url = "172.20.0.10:27017"
elif stage == "production":
    # --- parameter for porduction mode
    # keycloak settings
    keycloak_server_url = "http://172.20.0.3/auth/"  # traefik ip because kecloak is set PROXY_ADRESS_FORWARDING = True
    client_secret_key = "lpVjKsFc73HmrAu0FTMF9jq28nktxuvX"
    # mongo db url
    db_url = "172.20.0.10:27017"


def dave_settings():
    """
    This function returns a dictonary with the DaVe settings for used data and assumptions
    """
    settings = {
        # main definitions
        "dave_dir": os.path.dirname(os.path.realpath(__file__)),
        "dave_output_dir": os.path.expanduser(r"~\Desktop\DaVe_output"),
        "stage": stage,
        # database definitions (mongo db)
        "db_user": "dave_db_admin",
        "db_pw": "RxOPwwnahGhIKwLLhPH2",
        "db_ip": db_url,
        # authentification definitions
        "keycloak_server_url": keycloak_server_url,
        "client_id": "dave_login",
        "realm_name": "dave",
        "client_secret_key": client_secret_key,
        # structural definitions:
        "bar_format": "{desc:<10}{percentage:5.0f}%|{bar:30}| completed",  # format progress bar
        # geographical defintions:
        "crs_main": "EPSG:4326",  # crs which is based on the unit degree
        "crs_meter": "EPSG:3035",  # crs which is based on the unit meter
        # --- data request
        # OEP tables (oep_name:(schema, geometry_parameter, latest_version))
        "oep_tables": {
            "ego_pf_hv_bus": ("grid", "geom", "version=v0.4.6"),
            "ego_pf_hv_line": ("grid", "geom", "version=v0.4.6"),
            "ego_dp_ehv_substation": ("grid", "polygon", "version=v0.4.5"),
            "ego_pf_hv_transformer": ("grid", "geom", "version=v0.4.6"),
            "ego_dp_hvmv_substation": ("grid", "polygon", "version=v0.4.5"),
            "ego_dp_mvlv_substation": ("grid", "geom", "version=v0.4.5"),
            "ego_renewable_powerplant": ("supply", None, None),
            "ego_conventional_powerplant": ("supply", None, None),
        },
        # osm time delay (because osm doesn't alowed more than 1 request per second)
        "osm_time_delay": 60,  # in seconds
        # osm considered area (data for this area will be downloaded and impplemented in database)
        "osm_area": "germany",
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
            "road_plot": (
                "highway",
                ["motorway", "trunk", "primary"],
                ["way"],
                ["geometry", "name", "id", "surface"],
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
                ["leisure", "landuse", "natural", "name", "geometry", "id", "surface"],
            ),
            "natural": (
                "natural",
                ["scrub", "grassland", "water", "wood"],
                ["way", "relation"],
                ["natural", "landuse", "leisure", "name", "geometry", "id", "surface"],
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
                ["name", "railway", "geometry", "tram", "train", "usage", "voltage", "id"],
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
        # --- assumptions at power grid generating:
        # mv level
        "mv_voltage": 20,
        # hours per year
        "h_per_a": 8760,
        # power factors for loads
        "cos_phi_residential": 0.95,  # induktiv
        "cos_phi_industrial": 0.75,  # induktiv
        "cos_phi_commercial": 0.75,  # induktiv
        # avarage load values for ehv, hv, and mv loads
        "residential_load": 2,  # in MW/km²
        "industrial_load": 10,  # in MW/km²
        "commercial_load": 3,  # in MW/km²
        # --- assumptions at pandapower convert:
        # lines standard types
        "mv_line_std_type": "NA2XS2Y 1x240 RM/25 12/20 kV",  # dummy value, must be changed
        "lv_line_std_type": "NAYY 4x150 SE",  # dummy value, must be changed
        # trafo parameters for ehv/ehv and  ehv/hv. The dummy values are based on the pandapower
        # standarttype "160 MVA 380/110 kV" which is the biggest model
        "trafo_vkr_percent": 0.25,  # dummy value
        "trafo_vk_percent": 12.2,  # dummy value
        "trafo_pfe_kw": 60,  # dummy value
        "trafo_i0_percent": 0.06,  # dummy value
        # trafo standard types
        "hvmv_trafo_std_type": "63 MVA 110/20 kV",  # dummy value, must be changed
        "mvlv_trafo_std_type": "0.63 MVA 20/0.4 kV",  # dummy value, must be changed
        # --- assumptions at gas grid generating:
        # hp level
        "hp_nodes_height_m": 1,  # dummy value, must be changed
        "hp_pipes_k_mm": float(0.1),  # value based on shutterwald data, must be changed
        "hp_pipes_tfluid_k": 273.15,  # dummy value , must be changed
        # --- assumptions at model utils:
        "min_number_nodes": 4,
    }
    return settings


def db_restriction():
    """
    This function returns a dictonary with database collection restrictions for specific users and
    the user role they need to access it
    """
    restriction = {
        # restrictions for the tu berlin gas grid data
        # "postalcodes": "transhyde",  # example
    }
    return restriction
