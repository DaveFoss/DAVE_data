# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.


from geopandas import GeoDataFrame, read_file
from pandas import DataFrame, concat
from shapely.geometry import Polygon
from tqdm import tqdm

from dave_data.io.file_io import from_json_string
from dave_data.archiv_io import archiv_inventory
from src.dave_data.datapool.read_data import read_federal_states, read_nuts_regions, read_postal
from dave_data.geography.osm_data import from_osm, road_junctions
from dave_data.settings import dave_settings
from dave_data.toolbox import intersection_with_area


def _target_by_postalcode(grid_data, postalcode):
    """
    This function filter the postalcode informations for the target area.
    Multiple postalcode areas will be combinated.
    """
    postal, meta_data = read_postal()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    if len(postalcode) == 1 and postalcode[0].lower() == "all":
        # in this case all postalcode areas will be choosen
        target = postal
    else:
        target = postal[postal.postalcode.isin(postalcode)].reset_index(drop=True)
        # sort postalcodes
        postalcode.sort()
    return target


def _target_by_own_area(grid_data, own_area):
    """
    This function define the target area by a own area from the user. This could be a shapefile or
    directly a polygon. Furthermore the function filter the postalcode informations for the target area.
    """
    if isinstance(own_area, str):
        if own_area[-3:] == "shp":
            target = read_file(own_area)
        else:
            target = from_json_string(own_area)
        # check if the given shape file is empty
        if target.empty:
            print("The given shapefile includes no data")
    elif isinstance(own_area, Polygon):
        target = GeoDataFrame(
            {"name": ["own area"], "geometry": [own_area]}, crs=dave_settings["crs_main"]
        )
    else:
        print("The given format is unknown")

    # check crs and project to the right one if needed
    if (target.crs) and (target.crs != dave_settings["crs_main"]):
        target = target.to_crs(dave_settings["crs_main"])
    if "id" in target.keys():
        target = target.drop(columns=["id"])
    # convert own area into postal code areas for target_input
    postal, meta_data = read_postal()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(postal, target, remove_columns=False)
    # filter duplicated postal codes
    own_postal = postal_intersection["postalcode"].unique().tolist()
    return target, own_postal


def _target_by_town_name(grid_data, town_name):
    """
    This function filter the postalcode informations for the target area.
    Multiple town name areas will be combinated
    """
    postal, meta_data = read_postal()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    if len(town_name) == 1 and town_name[0].lower() == "all":
        # in this case all city names will be choosen (same case as all postalcode areas)
        target = postal
    else:
        # bring town names in right format and filter data
        normalized_town_names = [town.lower() for town in town_name]
        normalized_postal_town = postal.town.str.lower()
        indexes = normalized_postal_town.isin(normalized_town_names)
        target = postal[indexes].reset_index(drop=True)
        if len(target.town.unique()) != len(town_name):
            raise ValueError("town name wasn`t found. Please check your input")
        # sort town names
        town_name.sort()
    return target, town_name


def _target_by_federal_state(grid_data, federal_state):
    """
    This function filter the federal state informations for the target area.
    Multiple federal state areas will be combinated.
    """
    states, meta_data = read_federal_states()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    if len(federal_state) == 1 and federal_state[0].lower() == "all":
        # in this case all federal states will be choosen
        target = states
    else:
        # bring federal state names in right format and filter data
        federal_state = [
            "-".join(list(map(lambda x: x.capitalize(), state.split("-"))))
            for state in federal_state
        ]
        target = states[states["name"].isin(federal_state)].reset_index(drop=True)
        if len(target) != len(federal_state):
            raise ValueError("federal state name wasn`t found. Please check your input")
        # sort federal state names
        federal_state.sort()
    # convert federal states into postal code areas for target_input
    postal, meta_data = read_postal()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(postal, target, remove_columns=False)
    # filter duplicated postal codes
    federal_state_postal = postal_intersection["postalcode"].unique().tolist()
    return target, federal_state, federal_state_postal


def _target_by_nuts_region(grid_data, nuts_region):
    """
    This function filter the nuts region informations for the target area.
    """
    # check user input
    if isinstance(nuts_region, list):
        nuts_region = (nuts_region, "2016")  # default year
    # read nuts-3 areas
    nuts, meta_data = read_nuts_regions(year=nuts_region[1])
    nuts_3 = nuts[nuts.LEVL_CODE == 3]
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    if len(nuts_region[0]) == 1 and nuts_region[0][0].lower() == "all":
        # in this case all nuts_regions will be choosen
        target = nuts_3
    else:
        # bring NUTS ID in right format
        nuts_regions = list(
            map(
                lambda x: "".join(
                    [letter.upper() if letter.isalpha() else letter for letter in list(x)]
                ),
                nuts_region[0],
            )
        )
        nuts_region = (nuts_regions, nuts_region[1])
        for i, region in enumerate(nuts_region[0]):
            # get area for nuts region
            nuts_contains = nuts_3[nuts_3["NUTS_ID"].str.contains(region)]
            target = nuts_contains if i == 0 else concat([target, nuts_contains], ignore_index=True)
            if nuts_contains.empty:
                raise ValueError("nuts region name wasn`t found. Please check your input")
    # filter duplicates
    target.drop_duplicates(inplace=True)
    # convert nuts regions into postal code areas for target_input
    postal, meta_data = read_postal()
    # add meta data
    if f"{meta_data['Main'].Titel.loc[0]}" not in grid_data.meta_data.keys():
        grid_data.meta_data[f"{meta_data['Main'].Titel.loc[0]}"] = meta_data
    # filter postal code areas which are within the target area
    postal_intersection = intersection_with_area(postal, target, remove_columns=False)
    # filter duplicated postal codes
    nuts_region_postal = postal_intersection["postalcode"].unique().tolist()
    return target, nuts_region_postal


def target_area(
    grid_data,
    power_levels,
    gas_levels,
    postalcode=None,
    town_name=None,
    federal_state=None,
    nuts_region=None,
    own_area=None,
    buffer=0,
    roads=True,
    roads_plot=True,
    buildings=True,
    landuse=True,
    railways=True,
    waterways=True,
):
    """
    This function calculate all relevant geographical informations for the
    target area and add it to the grid_data

    INPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure
        **power_levels** (list)  - this parameter defines which power levels should be considered
                                   options: 'ehv','hv','mv','lv', [].
                                   there could be choose: one level, multiple levels or 'ALL'
        **gas_levels** (list)    - this parameter defines which gas levels should be considered
                                   options: 'hp','mp','lp', [].
                                   there could be choose: one level, multiple levels or 'ALL'

        One of these parameters must be set:
        **postalcode** (List of strings) - numbers of the target postalcode areas.
                                           it could also be choose ['ALL'] for all postalcode areas
                                           in germany
        **town_name** (List of strings) - names of the target towns
                                          it could also be choose ['ALL'] for all citys in germany
        **federal_state** (List of strings) - names of the target federal states
                                              it could also be choose ['ALL'] for all federal states
                                              in germany
        **nuts_region** (List of strings) - codes of the target nuts regions
                                              it could also be choose ['ALL'] for all nuts regions
                                              in europe
        **own_area** (string) - full path to a shape file which includes own target area
                                (e.g. "C:/Users/name/test/test.shp") or Geodataframe as string

    OPTIONAL:
        **buffer** (float, default 0) - buffer for the target area
        **roads** (boolean, default True) - obtain informations about roads which are relevant for
                                            the grid model
        **roads_plot** (boolean, default False) - obtain informations about roads which can be nice
                                                  for the visualization
        **buildings** (boolean, default True) - obtain informations about buildings
        **landuse** (boolean, default True) - obtain informations about landuses
        **railway** (boolean, default True) - obtain informations about railways
        **waterways** (boolean, default True) - obtain informations about waterways

    OUTPUT:

    EXAMPLE:
            from dave_data.topology import target_area
            target_area(town_name = ['Kassel'], buffer=0)
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="collect geographical data:         ",
        position=0,
        bar_format=dave_settings["bar_format"],
    )
    # check wich input parameter is given
    if postalcode:
        target = _target_by_postalcode(
            grid_data,
            postalcode,
        )
        target_input = DataFrame(
            {
                "typ": "postalcode",
                "data": [postalcode],
                "power_levels": [power_levels],
                "gas_levels": [gas_levels],
            }
        )
        grid_data.target_input = target_input
    elif town_name:
        target, town_name = _target_by_town_name(grid_data, town_name)
        target_input = DataFrame(
            {
                "typ": "town name",
                "data": [town_name],
                "power_levels": [power_levels],
                "gas_levels": [gas_levels],
            }
        )
        grid_data.target_input = target_input
    elif federal_state:
        target, federal_state, federal_state_postal = _target_by_federal_state(
            grid_data, federal_state
        )
        target_input = DataFrame(
            {
                "typ": "federal state",
                "federal_states": [federal_state],
                "data": [federal_state_postal],
                "power_levels": [power_levels],
                "gas_levels": [gas_levels],
            }
        )
        grid_data.target_input = target_input
    elif nuts_region:
        target, nuts_region_postal = _target_by_nuts_region(grid_data, nuts_region)
        target_input = DataFrame(
            {
                "typ": "nuts region",
                "nuts_regions": [nuts_region],
                "data": [nuts_region_postal],
                "power_levels": [power_levels],
                "gas_levels": [gas_levels],
            }
        )
        grid_data.target_input = target_input
    elif own_area:
        target, own_postal = _target_by_own_area(grid_data, own_area)
        target_input = DataFrame(
            {
                "typ": "own area",
                "data": [own_postal],
                "power_levels": [power_levels],
                "gas_levels": [gas_levels],
            }
        )
        grid_data.target_input = target_input
    else:
        raise SyntaxError("target area wasn`t defined")
    # write area informations into grid_data
    grid_data.area = concat([grid_data.area, target], ignore_index=True)
    if grid_data.area.crs is None:
        grid_data.area.set_crs(dave_settings["crs_main"], inplace=True)
    elif grid_data.area.crs != dave_settings["crs_main"]:
        grid_data.area.to_crs(dave_settings["crs_main"], inplace=True)
    # check if requested model is already in the archiv
    if not grid_data.target_input.iloc[0].typ == "own area":
        file_exists, file_name = archiv_inventory(grid_data, read_only=True)
    else:
        file_exists, file_name = False, "None"
    # update progress
    pbar.update(float(10))
    if not file_exists:
        # create borders for target area, load osm-data and write into grid data
        if town_name:
            diff_targets = target["town"].drop_duplicates()
            # define progress step
            progress_step = 80 / len(diff_targets)
            for diff_target in diff_targets:
                town = target[target.town == diff_target]
                target_geom = town.geometry.unary_union if len(town) > 1 else town.iloc[0].geometry
                # Obtain data from OSM
                from_osm(
                    grid_data,
                    pbar,
                    roads,
                    roads_plot,
                    buildings,
                    landuse,
                    railways,
                    waterways,
                    target_geom=target_geom,
                    progress_step=progress_step,
                )
        else:
            for i in range(0, len(target)):
                # define progress step
                progress_step = 80 / len(target)
                target_geom = target.geometry.iloc[i]
                # Obtain data from OSM
                from_osm(
                    grid_data,
                    pbar,
                    roads,
                    roads_plot,
                    buildings,
                    landuse,
                    railways,
                    waterways,
                    target_geom=target_geom,
                    progress_step=progress_step,
                )
        # reset index for all osm data
        grid_data.roads.roads.reset_index(drop=True, inplace=True)
        grid_data.roads.roads_plot.reset_index(drop=True, inplace=True)
        grid_data.landuse.reset_index(drop=True, inplace=True)
        grid_data.buildings.residential.reset_index(drop=True, inplace=True)
        grid_data.buildings.commercial.reset_index(drop=True, inplace=True)
        # find road junctions
        if "lv" in grid_data.target_input.power_levels[0]:
            road_junctions(grid_data)
        # close progress bar
        pbar.update(float(10))
        pbar.close()
        return file_exists, file_name
    else:
        # close progress bar
        pbar.update(float(90))
        pbar.close()
        return file_exists, file_name
