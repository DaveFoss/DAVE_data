# must import:
import os
import timeit

#from dave.create import create_grid
from dave.topology import target_area
from dave.plotting import plot_target_area, plot_grid_data
from dave.topology import create_lv_topology, create_hv_topology, create_ehv_topology
from dave.model import create_power_grid
from dave.components import power_components
from dave.datapool import oep_request
from dave.create import create_grid, create_empty_dataset
from dave.voronoi import voronoi
from dave.settings import dave_settings


# imports for tests:
#from dave import dave_dir
#import dave.datapool as data
from dave.datapool import read_ehv_data
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely.geometry
import shapely.ops
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.ops import cascaded_union, nearest_points
from shapely.geometry import Point, MultiPoint
import pandas as pd
import pandapower.plotting as pplt
import requests
from geopy.geocoders import ArcGIS
import numpy as np
from shapely.wkb import dumps, loads


"""
This is a example file for testing dave
"""

# start runtime
_start_time = timeit.default_timer()


########## testing Input Settings #########################
# test target by plz
_postalcode_1=['34225']
_postalcode_2=['37085', '37075', '37083', '37079', '37081', '37073', '37077']  # Göttingen
_postalcode_3=['ALL']

# test target by town_name
_town_name_1=['Baunatal']
_town_name_11=['Göttingen']
_town_name_2=['KAsSel', 'Baunatal']
_town_name_3=['ALL']

# test target by federal state
_federal_state_1=['Hessen']  
_federal_state_2=['HeSsEn', 'SchleSWIg-HOLstein']
_federal_state_3=['ALL']
_federal_state_NB1=['Baden-Württemberg']  # Transnet BW Gebiet
_federal_state_NB2=['Thüringen', 'Sachsen', 'Sachsen-Anhalt', 'Brandenburg', 
                    'Berlin', 'Mecklenburg-Vorpommern', 'Hamburg']  # 50 Hertz Gebiet

# test own shape (Hertingshausen is a part from the Town Baunatal). 
# It has 500 relevant Buildings(for living and commercial))
_own_area = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'

# own shape transnet
_own_area_tn = os.path.dirname(os.path.realpath(__file__))+'\\transnet\\transnet.shp'

# own shape test ehv
_own_area_test = os.path.dirname(os.path.realpath(__file__))+'\\test ehv\\test_ehv.shp'



##################### test with main function ##########################
"""
grid_data = create_grid(postalcode=None, 
                       town_name=None, 
                       federal_state=None, 
                       own_area=_own_area_tn,
                       power_levels=['HV'], 
                       gas_levels=[], 
                       plot=False, 
                       convert = False)
"""
#"""
grid_data  = create_grid(postalcode=None, 
                                    town_name=None, 
                                    federal_state=['Hessen'], 
                                    own_area=None,
                                    power_levels=['EHV', 'HV'],
                                    gas_levels=[], 
                                    plot=False, 
                                    convert = False)
#"""
"""
grid_data  = create_grid(postalcode=None, 
                                    town_name=None, 
                                    federal_state=None, 
                                    own_area=_own_area,
                                    power_levels=['LV'],
                                    gas_levels=[], 
                                    plot=True, 
                                    convert = False,
                                    opt_model = False)
"""
"""
grid_data  = create_grid(postalcode=None, 
                                    town_name=None, 
                                    federal_state=['ALL'], 
                                    own_area=None,
                                    power_levels=[],
                                    gas_levels=['HP'], 
                                    plot=True, 
                                    convert = False,
                                    opt_model = False)
"""




###################### Test manuel ##########################################
"""
# create empty datastructure
grid_data = create_empty_dataset()

# create target area
target_area(grid_data, own_area=_path, buffer=0).target()

# plot target area
plot_target_area(grid_data=grid_data)


# ---create low voltage topology:
create_lv_topology(grid_data=grid_data)

# --- create power components:
power_components(grid_data)

# plot target area with grid data
plot_grid_data(grid_data=grid_data)

# ---create pandapower model
net_power = create_power_grid(grid_data)

# plotting testweise, später mal selbst richtig machen mit angepassten farben usw. 
#pplt.simple_plot(net_power, line_width=1.5, bus_size=0.15)

"""

    

# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(round((_stop_time - _start_time)/60,2)) + 'min')

"""
# check time for special command
# start runtime
_start_time = timeit.default_timer()

        grid_data.lv_data.lv_lines.at[line.name, 'to_bus'] = dave_name

# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(_stop_time - _start_time) + 'sek')
"""