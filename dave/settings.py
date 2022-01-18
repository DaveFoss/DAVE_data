import os

# switch develop and production parameters
develop = True  # set True for develop modus
if develop:
    db_ip = "127.0.0.1:27017"  # database url in develop version
    keycloak_ip = "http://127.0.0.1/auth/"  # Keycloak url in develop version
else:
    db_ip = "172.20.0.10:27017"  # database url in production version
    keycloak_ip = "http://keycloak:8080/auth"  # Keycloak url in production version


def dave_settings():
    """
    This function returns a dictonary with the DaVe settings for used data and assumptions
    """
    settings = {
        # main definitions
        "dave_dir": os.path.dirname(os.path.realpath(__file__)),
        "dave_output_dir": os.path.expanduser(r"~\Desktop\DaVe_output"),
        # database definitions (mongo db)
        "db_user": "root",
        "db_pw": "example",
        "db_ip": db_ip,
        # authentication definitions (keycloak)
        "keycloak_ip": keycloak_ip,
        "client_id": "dave_login",
        "realm_name": "dave",
        "client_secret_key": "088d3f9e-58ea-405c-acf9-bf96b97ed922",
        # structural definitions:
        "bar_format": "{desc:<10}{percentage:5.0f}%|{bar:30}| completed",  # format progress bar
        # geographical defintions:
        "crs_main": "EPSG:4326",  # crs which is based on the unit degree
        "crs_meter": "EPSG:3035",  # crs which is based on the unit meter
        # --- data request
        # OEP versions:
        "hv_buses_ver": "version=v0.4.6",
        "hv_line_ver": "version=v0.4.6",
        "ehv_sub_ver": "version=v0.4.5",
        "ehvhv_trans_ver": "version=v0.4.6",
        "hvmv_sub_ver": "version=v0.4.5",
        "mvlv_sub_ver": "version=v0.4.5",
        # osm time delay (because osm doesn't alowed more than 1 request per second)
        "osm_time_delay": 60,  # in seconds
        # osm tags:
        "road_tags": 'highway~"secondary|tertiary|unclassified|residential|living_street|footway"',
        "road_plot_tags": 'highway~"motorway|trunk|primary"',
        "landuse_tags": 'landuse~"commercial|industrial|residential|retail"',
        "building_tags": "building",
        # osm categories
        "buildings_for_living": [
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
        # --- assumptions at grid generating:
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
    }
    return settings
