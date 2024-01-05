import geopandas as gpd
from dave.toolbox import get_data_path


def request_heat_demand(grid_data, output_folder, api_use):
    # the following lines retrieve the vector layer of HotMaps heat demand of Germany for any specific area of interest
    _heat_demand_path = get_data_path("heat_tot_curr_density/heat_tot_curr_density_DE_4326.shp", "data")
    grid_data.heat.demand = gpd.GeoDataFrame.from_file(_heat_demand_path, mask=grid_data.area)

   







