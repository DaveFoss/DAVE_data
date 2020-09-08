import geopandas as gpd
import copy
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import linemerge

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
    mvlv_buses = mvlv_buses.drop(columns=(['la_id', 'geom', 'subst_id', 'is_dummy', 'subst_cnt']))
    mvlv_buses = mvlv_buses.rename(columns={'version': 'ego_version',
                                            'mvlv_subst_id': 'ego_subst_id'})
    # change wrong crs from oep
    mvlv_buses.crs = 'EPSG:3035'
    mvlv_buses = mvlv_buses.to_crs(epsg=4326)
    # filter trafos for target area
    mvlv_buses = gpd.overlay(mvlv_buses, grid_data.area, how='intersection')
    if not mvlv_buses.empty:
        remove_columns = grid_data.area.keys().tolist()
        remove_columns.remove('geometry')
        mvlv_buses = mvlv_buses.drop(columns=remove_columns)
    mvlv_buses['node_type'] = 'mvlv_substation'
    # nodes for hv/mv trafos us side
    hvmv_buses = oep_request(schema='grid',
                             table='ego_dp_hvmv_substation',
                             where=dave_settings()['hvmv_sub_ver'],
                             geometry='point')
    hvmv_buses = hvmv_buses.rename(columns={'version': 'ego_version',
                                            'subst_id': 'ego_subst_id'})
    # filter trafos for target area
    hvmv_buses = gpd.overlay(hvmv_buses, grid_data.area, how='intersection')
    if not hvmv_buses.empty:
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
        mv_buses['voltage_kv'] = dave_settings()['mv_voltage']
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
        # lines to connect node with the nearest node
        mv_lines = gpd.GeoSeries([], crs='EPSG:4326')
        for i, bus in mv_buses.iterrows():
            mv_buses_rel = mv_buses.drop([bus.name])
            distance = mv_buses_rel.geometry.distance(bus.geometry)
            nearest_bus_idx = distance[distance == distance.min()].index[0]
            mv_line = LineString([bus.geometry, mv_buses.loc[nearest_bus_idx].geometry])
            # check if line already exists
            if not mv_lines.geom_equals(mv_line).any():
                mv_lines[i] = mv_line
        mv_lines = mv_lines.reset_index(drop=True)
        # connect line segments with each other
        while True:
            # search for related lines and merge them
            mv_lines_rel = copy.deepcopy(mv_lines)
            for i, bus in mv_buses.iterrows():
                # check if bus is conected to more than one line
                lines_intersect = mv_lines_rel[mv_lines_rel.intersects(bus.geometry)]
                if len(lines_intersect) > 1:
                    # get list with line objects
                    lines_list = lines_intersect.tolist()
                    # search for multilines and split them
                    new_line = []
                    for line in lines_list:
                        if isinstance(line, MultiLineString):
                            for segment in line:
                                new_line.append(segment)
                        else:
                            new_line.append(line)
                    # merge found lines and add new line to line quantity
                    line_related = linemerge(new_line)
                    mv_lines_rel[len(mv_lines)] = line_related
                    # delete found lines from line quantity
                    mv_lines_rel = mv_lines_rel.drop(lines_intersect.index.tolist())
                    mv_lines_rel = mv_lines_rel.reset_index(drop=True)
            # break loop if all lines connected
            if len(mv_lines_rel) == 1:
                break
            # create lines for connecting line segments
            for i, line in mv_lines_rel.iteritems():
                # find nearest line to considered one
                mv_lines_con = mv_lines_rel.drop([i])
                distance = mv_lines_con.geometry.distance(line)
                nearest_line_idx = distance[distance == distance.min()].index[0]
                # get line coordinates
                line_points = gpd.GeoSeries([], crs='EPSG:4326')
                if isinstance(line, MultiLineString):
                    k = 0
                    for segment in line:
                        for j in range(0, len(segment.coords[:])):
                            point = segment.coords[:][j]
                            line_points[k] = Point(point)
                            k += 1
                else:
                    for j in range(0, len(line.coords[:])):
                        point = line.coords[:][j]
                        line_points[j] = Point(point)
                # get nearest line coordinates
                nearest_line_points = gpd.GeoSeries([], crs='EPSG:4326')
                nearest_line = mv_lines_rel.loc[nearest_line_idx]
                if isinstance(nearest_line, MultiLineString):
                    k = 0
                    for segment in nearest_line:
                        for j in range(0, len(segment.coords[:])):
                            point = segment.coords[:][j]
                            nearest_line_points[k] = Point(point)
                            k += 1
                else:
                    for j in range(0, len(nearest_line.coords[:])):
                        point = mv_lines_rel.loc[nearest_line_idx].coords[:][j]
                        nearest_line_points[j] = Point(point)
                distance_min = 1000  # any big number for initialize
                # find pair of nearest nodes
                for j in range(0, len(line_points)):
                    point = line_points[j]
                    distance = nearest_line_points.geometry.distance(point)
                    if distance_min > distance.min():
                        distance_min = distance.min()
                        nearest_point_idx = distance[distance == distance.min()].index[0]
                        nearest_point = nearest_line_points[nearest_point_idx]
                        line_point = line_points[j]
                # add createt connection line into mv lines
                mv_line = LineString([line_point, nearest_point])
                if not mv_lines.geom_equals(mv_line).any():
                    mv_lines[len(mv_lines)] = mv_line
        # prepare dataframe for mv lines
        mv_lines = gpd.GeoDataFrame(geometry=mv_lines)
        mv_lines.insert(0, 'dave_name', None)
        # project lines to crs with unit in meter for length calculation
        mv_lines_3035 = mv_lines.to_crs(epsg=3035)
        # add parameters to lines
        for i, line in mv_lines.iterrows():
            # from bus name
            from_bus = line.geometry.coords[:][0]
            from_bus_distance = mv_buses.distance(Point(from_bus))
            from_bus_idx = from_bus_distance[from_bus_distance == from_bus_distance.min()].index[0]
            from_bus_name = mv_buses.loc[from_bus_idx].dave_name
            mv_lines.at[line.name, 'from_bus'] = from_bus_name
            # to bus name
            to_bus = line.geometry.coords[:][1]
            to_bus_distance = mv_buses.distance(Point(to_bus))
            to_bus_idx = to_bus_distance[to_bus_distance == to_bus_distance.min()].index[0]
            to_bus_name = mv_buses.loc[to_bus_idx].dave_name
            mv_lines.at[line.name, 'to_bus'] = to_bus_name
            # calculate length in km
            line_length_km = mv_lines_3035.loc[i].geometry.length/1000
            mv_lines.at[line.name, 'length_km'] = line_length_km
            # line dave name
            mv_lines.at[line.name, 'dave_name'] = f'line_5_{i}'
            # additional informations
            mv_lines.at[line.name, 'voltage_kv'] = dave_settings()['mv_voltage']
            mv_lines.at[line.name, 'voltage_level'] = 5
            mv_lines.at[line.name, 'source'] = 'dave internal'
        # add mv nodes to grid data
        grid_data.mv_data.mv_lines = grid_data.mv_data.mv_lines.append(mv_lines)
