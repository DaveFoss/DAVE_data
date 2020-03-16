# must import:
import os
import timeit

from dave.topology import target_area
from dave.plotting import plot_target_area, plot_grid_data
from dave.topology import create_lv_topology
from dave.model import create_power_grid



# imports for tests:
#from dave import dave_dir
import dave.datapool as data
import geopandas as gpd
import geopandas_osm.osm
import matplotlib.pyplot as plt
import shapely.geometry
import shapely.ops
import pandas as pd
import pandapower.plotting as pplt
import requests


"""
This is a example file for testing dave
"""

# start runtime
_start_time = timeit.default_timer()

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
_path = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'
target_area = target_area(own_area=_path, buffer=0).target()

# plot target area
#plot_target_area(target_area=target_area)


# ---create low voltage topology:
print('create low voltage network for target area')
print('------------------------------------------')
grid_data = create_lv_topology(target_area=target_area)

# plot target area with grid data
plot_grid_data(grid_data=grid_data)

# ---create pandapower model
print('create pandapower network for target area')
print('------------------------------------------')
power_grid = create_power_grid(grid_data)
# plotting testweise, später mal selbst richtig machen mit angepassten farben usw. 
pplt.simple_plot(power_grid, line_width=1.5, bus_size=0.15)




"""
# ---test mv/lv trafos openego
# oedb
oep_url= 'http://oep.iks.cs.ovgu.de/'

# select opsd renewable power plants
schema='grid'
table='ego_dp_mvlv_substation'
where = 'version=v0.2.8'  

trafo = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where, )
trafo.status_code

# convert to dataframe
df_pp = pd.DataFrame(trafo.json())

# --- convert to geopandas with right crs
# transform WKB to WKT / Geometry
df_pp['geom'] = df_pp['geom'].apply(lambda x:shapely.wkb.loads(x, hex=True))
# create geoDataFrame
crs = {'init' :'epsg:3035'}
gdf_pp = gpd.GeoDataFrame(df_pp, crs=crs, geometry=df_pp.geom)
gdf_pp_4326 = gdf_pp.to_crs(epsg=4326)
# filter trafos for target area
trafo_intersection = gpd.overlay(gdf_pp_4326, target_area['area'], how='intersection').geometry

""" 




# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(round((_stop_time - _start_time)/60,2)) + 'min')