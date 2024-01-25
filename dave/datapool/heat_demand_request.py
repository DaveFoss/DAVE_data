# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from geopandas import GeoDataFrame

from dave.toolbox import get_data_path


def request_heat_demand(grid_data):
    # the following lines retrieve the vector layer of HotMaps heat demand of Germany for any specific area of interest
    _heat_demand_path = get_data_path(
        "heat_tot_curr_density/heat_tot_curr_density_DE_4326.shp", "data"
    )
    grid_data.heat.demand = GeoDataFrame.from_file(_heat_demand_path, mask=grid_data.area)
