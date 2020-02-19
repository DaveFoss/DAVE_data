# must import:
import os
import timeit

from dave.topology import target_area
from dave.plotting import plot_target_area, plot_grid_data
from dave.topology import create_lv_topology
from dave import dave_dir


# imports for tests:
import dave.datapool as data
import geopandas as gpd
import geopandas_osm.osm
import matplotlib.pyplot as plt
import shapely.geometry


"""
This is a example file for testing dave
"""

# start runtime
start_time = timeit.default_timer()

# --- testing target area
print('Check OSM data for target area')
print('------------------------------')

# test target by plz
#target_area  = target_area(postalcode=['34225']).target()
#target_area  = target_area(postalcode=['34225', '34311']).target()

# test target by town_name
#target_area =target_area(town_name=['Baunatal']).target()
#target_area =target_area(town_name=['KAsSel', 'Baunatal']).target()

# test target by federal state
#target_area = target_area(federal_state=['Hessen']).target()
#target_area =target_area(federal_state=['HeSsEn', 'SchleSWIg-HOLstein']).target()

# test own shape (Hertingshausen is a part from the Town Baunatal. It has 500 relevant Buildings(for living and commercial))
path = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'
target_area = target_area(own_area=path, buffer=0).target()

# plot target area
#plot_target_area(target_area=target_area)



# create low voltage topology:
print('create low voltage network for target area')
print('------------------------------------------')
grid_data_lv = create_lv_topology(target_area=target_area)

# plot target area with grid data
plot_grid_data(grid_data=grid_data_lv)



# plot building to raod connections
#line_buildings.plot(ax=ax, color='m')




# stop and show runtime
stop_time = timeit.default_timer()
print('runtime = ' + str(round((stop_time - start_time),2)) + 's')