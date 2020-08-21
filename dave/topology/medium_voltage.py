import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

from dave.datapool import oep_request
from dave.settings import dave_settings

def create_mv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    medium voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:

    EXAMPLE:
    """
    # print to inform user
    print('create medium voltage network for target area')
    print('---------------------------------------------')
    
    # --- create mv nodes
    # nodes for mv/lv traofs hv side
    mvlv_buses = oep_request(schema='grid',
                             table='ego_dp_mvlv_substation',
                             where=dave_settings()['mvlv_sub_ver'],
                             geometry='geom')
    mvlv_buses = mvlv_buses.rename(columns={'version': 'ego_version'})
    # change wrong crs from oep
    mvlv_buses.crs = 'EPSG:3035'
    mvlv_buses = mvlv_buses.to_crs(epsg=4326)
    # filter trafos for target area
    mvlv_buses = gpd.overlay(mvlv_buses, grid_data.area, how='intersection')
    if not mvlv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove('geometry')
        mvlv_buses = mvlv_buses.drop(columns=remove_columns)
    mvlv_buses = mvlv_buses.drop(columns=(['la_id', 'geom', 'subst_id', 'is_dummy', 'subst_cnt']))
    mvlv_buses['node_type'] = 'mvlv_substation'
    # nodes for hv/mv trafos us side
    hvmv_buses = oep_request(schema='grid', 
                             table='ego_dp_hvmv_substation', 
                             where='version=v0.4.5',
                             geometry='point')
    hvmv_buses = hvmv_buses.rename(columns={'version': 'ego_version'})
    # filter trafos for target area
    hvmv_buses = gpd.overlay(hvmv_buses, grid_data.area, how='intersection')
    if not mvlv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove('geometry')
        hvmv_buses = hvmv_buses.drop(columns=remove_columns)
    hvmv_buses = hvmv_buses.drop(columns=(['lon', 'lat', 'point', 'polygon', 'power_type',
                                           'substation', 'frequency', 'ref', 'dbahn', 'status',
                                           'ags_0', 'geom', 'voltage']))
    hvmv_buses['node_type'] = 'hvmv_substation'
    # consider data only if there are more than one node in the target area
    mv_buses = mvlv_buses.append(hvmv_buses)
    if len(mv_buses) > 1:
        mv_buses['voltage_level'] = 5
        mv_buses['voltage_kv'] = 20
        # add oep as source
        mv_buses['source'] = 'OEP'
        # add dave name
        mv_buses.insert(0, 'dave_name', None)
        mv_buses = mv_buses.reset_index(drop=True)
        for i, bus in mv_buses.iterrows():
            mv_buses.at[bus.name, 'dave_name'] = f'node_5_{i}'
        # add mv nodes to grid data
        grid_data.mv_data.mv_nodes = grid_data.mv_data.mv_nodes.append(mv_buses)
        
        
        
        # --- create mv lines
        # lines to connect node with the neares node
        mv_lines = gpd.GeoSeries([], crs='EPSG:4326')
        for i, bus in mv_buses.iterrows():
            mv_buses_rel = mv_buses.drop([bus.name])
            distance = mv_buses_rel.geometry.distance(bus.geometry)
            nearest_bus_idx = distance[distance == distance.min()].index[0]
            mv_line = LineString([bus.geometry, mv_buses.loc[nearest_bus_idx].geometry])
            # check if line already exists
            if not mv_lines.geom_equals(mv_line).any():
                mv_lines[i] = mv_line
        """
        # merge related lines
        for i, bus in mv_buses.iterrows():
            if 
            """
    
    
    
    
    """
    # calculate line length
    line_buildings_3035 = line_buildings.to_crs(epsg=3035)  # project lines to crs with unit in meter
    line_length = line_buildings_3035.length
    # write line informations into grid data
    grid_data.lv_data.lv_lines = grid_data.lv_data.lv_lines.append(gpd.GeoDataFrame({'geometry': line_buildings,
                                                                                     'line_type': 'line_buildings',
                                                                                     'length_km': line_length/1000,
                                                                                     'voltage_kv': 0.4,
                                                                                     'voltage_level': 7,
                                                                                     'source': 'dave internal'}))
    """
    
    
    
    
    # # --- test plot
    # fig = plt.figure(frameon=False, figsize=(50, 50))
    # ax = fig.add_subplot(1, 1, 1)
    # ax.axis('off')
    # ax = grid_data['area'].plot(color='k', alpha=0.1, ax=ax)
    # ax.margins(0)
    # # input data
    # roads_plot = grid_data.roads.roads_plot
    # roads = grid_data.roads.roads
    # road_junctions = grid_data.roads.road_junctions
    # """
    # # plot road informations
    # if not roads_plot.empty:
    #     # these highways are only relevant for plotting
    #     roads_plot.plot(ax=ax, color='k', label='Roads')  
    # if not roads.empty:
    #     roads.plot(ax=ax, color='k')
    # """
    # mv_buses.plot(ax=ax, color='m')
    # mv_lines.plot(ax=ax, color='b')
   
  

