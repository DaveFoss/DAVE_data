from dave.settings import dave_settings
from geopandas import GeoDataFrame
from geopandas import GeoSeries
from pandapower.auxiliary import ADict
from pandas import DataFrame


class davestructure(ADict):
    """
    This class is for the davestracture as attributed dictionary and to makes it possible to \
    showing a overview of the DAVE dataset in the python console
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(args[0], self.__class__):
            net = args[0]
            self.clear()
            self.update(**net.deepcopy())

    def __repr__(self):  # pragma: no cover
        titel = "This DAVE dataset includes the following parameter tables:"
        for key in list(self.keys()):
            if isinstance(self[key], DataFrame) and not self[key].empty:
                length = len(self[key])
                titel += f'\n   - {key} ({length} {"elements" if length > 1 else "element"})'
            if isinstance(self[key], davestructure):
                titel += f"\n   - {key}:"
                for key2 in list(self[key].keys()):
                    if (
                        isinstance(self[key][key2], DataFrame)
                        and not self[key][key2].empty
                    ):
                        length = len(self[key][key2])
                        titel += f'\n\t   - {key2} ({length} {"elements" if length > 1 else "element"})'
                    if isinstance(self[key][key2], davestructure):
                        titel += f"\n\t   - {key2}:"
                        for key3 in list(self[key][key2].keys()):
                            if (
                                isinstance(self[key][key2][key3], DataFrame)
                                and not self[key][key2][key3].empty
                            ):
                                length = len(self[key][key2][key3])
                                titel += f'\n\t\t   - {key3} ({length} {"elements" if length > 1 else "element"})'
        return titel


def create_empty_dataset():
    """
    This function initializes the dave datastructure and create all possible data categories

    OUTPUT:
        **grid_data** (attrdict) - dave attrdict with empty tables

    EXAMPLE:
        grid_data = create_empty_dataset()

    """
    # define dave structure
    grid_data = davestructure(
        {
            # target data
            "area": GeoDataFrame([]),
            "target_input": DataFrame(),
            "buildings": davestructure(
                {
                    "commercial": GeoDataFrame([]),
                    "residential": GeoDataFrame([]),
                    "other": GeoDataFrame([]),
                }
            ),
            "roads": davestructure(
                {
                    "roads": GeoDataFrame([]),
                    "road_junctions": GeoSeries([]),
                }
            ),
            "landuse": GeoDataFrame([]),
            "railways": GeoDataFrame([]),
            "waterways": GeoDataFrame([]),
            # power grid data
            "ehv_data": davestructure(
                {"ehv_nodes": GeoDataFrame([]), "ehv_lines": GeoDataFrame([])}
            ),
            "hv_data": davestructure(
                {"hv_nodes": GeoDataFrame([]), "hv_lines": GeoDataFrame([])}
            ),
            "mv_data": davestructure(
                {"mv_nodes": GeoDataFrame([]), "mv_lines": GeoDataFrame([])}
            ),
            "lv_data": davestructure(
                {"lv_nodes": GeoDataFrame([]), "lv_lines": GeoDataFrame([])}
            ),
            "components_power": davestructure(
                {
                    "loads": GeoDataFrame([]),
                    "renewable_powerplants": GeoDataFrame([]),
                    "conventional_powerplants": GeoDataFrame([]),
                    "transformers": davestructure(
                        {
                            "ehv_ehv": GeoDataFrame([]),
                            "ehv_hv": GeoDataFrame([]),
                            "hv_mv": GeoDataFrame([]),
                            "mv_lv": GeoDataFrame([]),
                        }
                    ),
                    "substations": davestructure(
                        {
                            "ehv_hv": GeoDataFrame([]),
                            "hv_mv": GeoDataFrame([]),
                            "mv_lv": GeoDataFrame([]),
                        }
                    ),
                }
            ),
            # gas grid data
            "hp_data": davestructure(
                {
                    "hp_junctions": GeoDataFrame([]),
                    "hp_pipes": GeoDataFrame([]),
                }
            ),
            "mp_data": davestructure(
                {
                    "mp_junctions": GeoDataFrame([]),
                    "mp_pipes": GeoDataFrame([]),
                }
            ),
            "lp_data": davestructure(
                {
                    "lp_junctions": GeoDataFrame([]),
                    "lp_pipes": GeoDataFrame([]),
                }
            ),
            "components_gas": davestructure(
                {
                    "compressors": GeoDataFrame([]),
                    "sinks": GeoDataFrame([]),
                    "sources": GeoDataFrame([]),
                    "storages_gas": GeoDataFrame([]),
                    "valves": GeoDataFrame([]),
                }
            ),
            # building height data
            "building_height": GeoDataFrame([]),
            # eubucco building characteristic
            "eubucco": davestructure(
                {
                    "building_height": GeoDataFrame([]),
                    "building_age": GeoDataFrame([]),
                    "building_type": GeoDataFrame([]),
                }
            ),
            # census data
            "census_data": davestructure(
                {
                    "population": GeoDataFrame([]),
                }
            ),
            # auxillary
            "dave_version": dave_settings["dave_version"],
            "meta_data": {},
        }
    )
    return grid_data
