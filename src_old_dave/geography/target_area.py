from dave.archiv_io import archiv_inventory
from dave.geography.osm_data import from_osm
from dave.geography.osm_data import road_junctions
from dave.io.file_io import from_json_string
from dave.settings import dave_settings
from dave.toolbox import intersection_with_area
from geopandas import GeoDataFrame
from pandas import DataFrame
from pandas import concat
from shapely.geometry import Polygon
from tqdm import tqdm


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
            from dave.topology import target_area
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
        target, nuts_region_postal = _target_by_nuts_region(
            grid_data, nuts_region
        )
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
                target_geom = (
                    town.geometry.unary_union
                    if len(town) > 1
                    else town.iloc[0].geometry
                )
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
            for i in range(len(target)):
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
