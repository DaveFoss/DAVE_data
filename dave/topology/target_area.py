import pandas as pd
import geopandas as gpd
import time
from shapely.ops import cascaded_union
from shapely.geometry import Polygon, LineString, Point

from dave.datapool import *
from dave.settings import dave_settings


class target_area():
    """
    This class contains functions to define a target area and getting all relevant osm data for it

    INPUT:
        **grid_data** (attrdict) - grid_data as a attrdict in dave structure
        **power_levels** (list)  - this parameter defines which power levels should be considered
                                   options: 'EHV','HV','MV','LV', [].
                                   there could be choose: one level, multiple levels or 'ALL'
        **gas_levels** (list)    - this parameter defines which gas levels should be considered
                                   options: 'HP','MP','LP', [].
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
        **own_area** (string) - full path to a shape file which includes own target area
                                (e.g. "C:/Users/name/test/test.shp")

    OPTIONAL:
        **buffer** (float, default 0) - buffer for the target area
        **roads** (boolean, default True) - obtain informations about roads which are relevant for
                                            the grid model
        **roads_plot** (boolean, default False) - obtain informations about roads which can be nice
                                                  for the visualization
        **buildings** (boolean, default True) - obtain informations about buildings
        **landuse** (boolean, default True) - obtain informations about landuses

    OUTPUT:

    EXAMPLE:
            from dave.topology import target_area
            target_area(town_name = ['Kassel'], buffer=0).target()
    """

    def __init__(self, grid_data, power_levels, gas_levels, postalcode=None, town_name=None,
                 federal_state=None, own_area=None, buffer=0, roads=True, roads_plot=True,
                 buildings=True, landuse=True):
        # Init input parameters
        self.grid_data = grid_data
        self.postalcode = postalcode
        self.town_name = town_name
        self.federal_state = federal_state
        self.own_area = own_area
        self.buffer = buffer
        self.roads = roads
        self.roads_plot = roads_plot
        self.buildings = buildings
        self.landuse = landuse
        self.power_levels = power_levels
        self.gas_levels = gas_levels

    def _from_osm(self, target, target_number=None, target_town=None):
        """
        This function searches for data on OpenStreetMap (OSM) and filters the relevant paramerters
        for grid modeling
        """
        # add time delay because osm doesn't alowed more than 1 request per second.
        time_delay = dave_settings()['osm_time_delay']
        # search relevant road informations in the target area
        if self.roads:
            roads = query_osm('way', target, recurse='down', tags=[dave_settings()['road_tags']])
            # check if there are data for roads
            if not roads.empty:
                # define road parameters which are relevant for the grid modeling
                relevant_columns = ['geometry', 'name', 'highway']
                roads = roads.filter(relevant_columns)
                # consider only the linestring elements
                roads = roads[roads.geometry.length != 0]
                # consider only roads which intersects the target area
                if target_number or target_number == 0:
                    target_area = self.target.geometry.iloc[target_number]
                elif target_town:
                    targets = self.target[self.target.town == target_town]
                    target_area = cascaded_union(targets.geometry.tolist())
                roads = roads[roads.geometry.intersects(target_area)]
                # write roads into grid_data
                roads = roads.set_crs(dave_settings()['crs_main'])
                self.grid_data.roads.roads = self.grid_data.roads.roads.append(roads)
            # add time delay
            time.sleep(time_delay)
        # search irrelevant road informations in the target area for a better overview
        if self.roads_plot:
            roads_plot = query_osm('way', target, recurse='down',
                                   tags=[dave_settings()['road_plot_tags']])
            # check if there are data for roads_plot
            if not roads_plot.empty:
                # define road parameters which are relevant for the grid modeling
                relevant_columns = ['geometry', 'name']
                roads_plot = roads_plot.filter(relevant_columns)
                # consider only the linestring elements
                roads_plot = roads_plot[roads_plot.geometry.length != 0]
                # consider only roads which intersects the target area
                if target_number or target_number == 0:
                    target_area = self.target.geometry.iloc[target_number]
                elif target_town:
                    targets = self.target[self.target.town == target_town]
                    target_area = cascaded_union(targets.geometry.tolist())
                roads_plot = roads_plot[roads_plot.geometry.intersects(target_area)]
                # write plotting roads into grid_data
                roads_plot = roads_plot.set_crs(dave_settings()['crs_main'])
                self.grid_data.roads.roads_plot = self.grid_data.roads.roads_plot.append(roads_plot)
            # add time delay
            time.sleep(time_delay)
        # search landuse informations in the target area
        if self.landuse:
            landuse = query_osm('way', target, recurse='down',
                                tags=[dave_settings()['landuse_tags']])
            # check additionally osm relations
            landuse_rel = query_osm('relation', target, recurse='down',
                                    tags=[dave_settings()['landuse_tags']])
            landuse_rel = landuse_rel.reset_index(drop=True)
            # add landuses from relations to landuses from ways
            landuse = landuse.append(landuse_rel)
            landuse = landuse.reset_index(drop=True)
            # check if there are data for landuse
            if not landuse.empty:
                # define landuse parameters which are relevant for the grid modeling
                relevant_columns = ['landuse', 'geometry', 'name']
                landuse = landuse.filter(relevant_columns)
                # consider only the linestring elements
                landuse = landuse[landuse.geometry.length != 0]
                # consider only landuses which intersects the target area
                if target_number or target_number == 0:
                    target_area = self.target.geometry.iloc[target_number]
                elif target_town:
                    targets = self.target[self.target.town == target_town]
                    target_area = cascaded_union(targets.geometry.tolist())
                # filter landuses that touches the target area
                landuse = landuse[landuse.geometry.intersects(target_area)]
                # convert geometry to polygon
                for i, land in landuse.iterrows():
                    if isinstance(land.geometry, LineString):
                        num_coords = len(land.geometry.coords[:])
                        # A LinearRing must have at least 3 coordinate tuples
                        if num_coords >= 3:
                            landuse.at[land.name, 'geometry'] = Polygon(land.geometry)
                        else:
                            landuse = landuse.drop([land.name])
                    elif isinstance(land.geometry, Point):
                        # delet landuse if geometry is a point
                        landuse = landuse.drop([land.name])
                # intersect landuses with the target area
                landuse = landuse.set_crs(dave_settings()['crs_main'])
                area = self.grid_data.area.rename(columns={'name': 'bundesland'})
                landuse = gpd.overlay(landuse, area, how='intersection')
                if not landuse.empty:
                    remove_columns = area.keys().tolist()
                    remove_columns.remove('geometry')
                    landuse = landuse.drop(columns=remove_columns)
                # calculate polygon area in km²
                landuse_3035 = landuse.to_crs(dave_settings()['crs_meter'])
                landuse_area = landuse_3035.area/1E06
                landuse['area_km2'] = landuse_area
                # write landuse into grid_data
                landuse = landuse.set_crs(dave_settings()['crs_main'])
                self.grid_data.landuse = self.grid_data.landuse.append(landuse)
            # add time delay
            time.sleep(time_delay)
        # search building informations in the target area
        if self.buildings:
            buildings = query_osm('way', target, recurse='down',
                                  tags=[dave_settings()['building_tags']])
            # check if there are data for buildings
            if not buildings.empty:
                # define building parameters which are relevant for the grid modeling
                relevant_columns = ['addr:housenumber', 'addr:street', 'addr:suburb', 'amenity',
                                    'building', 'building:levels', 'geometry', 'name']
                buildings = buildings.filter(relevant_columns)
                # consider only the linestring elements
                buildings = buildings[buildings.geometry.length != 0]
                # consider only buildings which intersects the target area
                if target_number or target_number == 0:
                    target_area = self.target.geometry.iloc[target_number]
                elif target_town:
                    targets = self.target[self.target.town == target_town]
                    target_area = cascaded_union(targets.geometry.tolist())
                buildings = buildings[buildings.geometry.intersects(target_area)]
                # create building categories
                for_living = dave_settings()['buildings_for_living']
                commercial = dave_settings()['buildings_commercial']
                # improve building tag with landuse parameter
                if not landuse.empty:
                    landuse_retail = cascaded_union(landuse[landuse.landuse == 'retail'].geometry)
                    landuse_industrial = cascaded_union(landuse[landuse.landuse == 'industrial'].geometry)
                    landuse_commercial = cascaded_union(landuse[landuse.landuse == 'commercial'].geometry)
                    for i, building in buildings.iterrows():
                        if building.building not in (commercial):
                            if building.geometry.intersects(landuse_retail):
                                buildings.at[i, 'building'] = 'retail'
                            elif building.geometry.intersects(landuse_industrial):
                                buildings.at[i, 'building'] = 'industrial'
                            elif building.geometry.intersects(landuse_commercial):
                                buildings.at[i, 'building'] = 'commercial'
                # write buildings into grid_data
                buildings = buildings.set_crs(dave_settings()['crs_main'])
                self.grid_data.buildings.for_living = self.grid_data.buildings.for_living.append(buildings[buildings.building.isin(for_living)])
                self.grid_data.buildings.commercial = self.grid_data.buildings.commercial.append(buildings[buildings.building.isin(commercial)])
                self.grid_data.buildings.other = self.grid_data.buildings.other.append(buildings[~buildings.building.isin(for_living+commercial)])
            # add time delay
            time.sleep(time_delay)

    def road_junctions(self):
        """
        This function searches junctions for the relevant roads in the target area
        """
        roads = self.grid_data.roads.roads
        if not roads.empty:
            junction_points = []
            while len(roads) > 1:
                # considered line
                line_geometry = roads.iloc[0].geometry
                # check considered line surrounding for possible intersectionpoints with other lines
                line_surr = line_geometry.buffer(1E-04)
                lines_rel = roads[roads.geometry.crosses(line_surr)]
                other_lines = cascaded_union(lines_rel.geometry)
                # find line intersections between considered line and other lines
                junctions = line_geometry.intersection(other_lines)
                if junctions.geom_type == 'Point':
                    junction_points.append(junctions)
                elif junctions.geom_type == 'MultiPoint':
                    for point in junctions:
                        junction_points.append(point)
                # set new roads quantity for the next iterationstep
                roads = roads.drop([0])
                roads = roads.reset_index(drop=True)
            # delet duplicates
            junction_points = gpd.GeoSeries(junction_points)
            road_junctions = junction_points.drop_duplicates()
            # write road junctions into grid_data
            road_junctions = road_junctions.set_crs(dave_settings()['crs_main'])
            self.grid_data.roads.road_junctions = road_junctions.rename('geometry')

    def _target_by_postalcode(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple postalcode areas will be combinated.
        """
        postal = read_postal()
        if len(self.postalcode) == 1 and self.postalcode[0] == 'ALL':
            # in this case all postalcode areas will be choosen
            target = postal
        else:
            for i in range(len(self.postalcode)):
                if i == 0:
                    target = postal[postal.postalcode == self.postalcode[i]]
                else:
                    target = target.append(postal[postal.postalcode == self.postalcode[i]])
            # sort federal state names
            self.postalcode.sort()
        self.target = target

    def _own_area_postal(self):
        """
        This functions searches for the postal codes which intersects with the own area
        """
        postal = read_postal()
        postal_intersection = gpd.overlay(postal, self.target, how='intersection')
        postal_list = postal_intersection['postalcode'].tolist()
        postal_filtered = []
        [postal_filtered.append(x) for x in postal_list if x not in postal_filtered]
        self.own_postal = postal_filtered

    def _target_by_town_name(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple town name areas will be combinated
        """
        postal = read_postal()
        if len(self.town_name) == 1 and self.town_name[0] == 'ALL':
            # in this case all city names will be choosen (same case as all postalcode areas)
            target = postal
        else:
            names_right = []
            for i in range(len(self.town_name)):
                if i == 0:
                    town_name = self.town_name[0].capitalize()
                    target = postal[postal.town == town_name]
                else:
                    town_name = self.town_name[i].capitalize()
                    target = target.append(postal[postal.town == town_name])
                names_right.append(town_name)
                if target.empty:
                    raise ValueError('town name wasn`t found. Please check your input')
            # sort federal state names
            names_right.sort()
            self.town_name = names_right
        self.target = target

    def _target_by_federal_state(self):
        """
        This function filter the federal state informations for the target area.
        Multiple federal state areas will be combinated.
        """
        states = read_federal_states()
        if len(self.federal_state) == 1 and self.federal_state[0] == 'ALL':
            # in this case all federal states will be choosen
            target = states
        else:
            names_right = []
            for i in range(len(self.federal_state)):
                # bring name in right form
                state_name = self.federal_state[i].split('-')
                if len(state_name) == 1:
                    state_name = state_name[0].capitalize()
                else:
                    state_name = state_name[0].capitalize()+'-'+state_name[1].capitalize()
                names_right.append(state_name)
                if i == 0:
                    target = states[states['name'] == state_name]
                else:
                    target = target.append(states[states['name'] == state_name])
                if target.empty:
                    raise ValueError('federal state name wasn`t found. Please check your input')
            # sort federal state names
            names_right.sort()
            self.federal_state = names_right
        self.target = target
        # convert federal states into postal code areas for target_input
        postal = read_postal()
        postal_intersection = gpd.overlay(postal, self.target, how='intersection')
        postal_list = postal_intersection['postalcode'].tolist()
        # filter duplicated postal codes
        postal_filtered = []
        [postal_filtered.append(x) for x in postal_list if x not in postal_filtered]
        self.federal_state_postal = postal_filtered

    def target(self):
        """
        This function calculate all relevant geographical informations for the
        target area and add it to the grid_data
        """
        # print to inform user
        print('Check OSM data for target area')
        print('------------------------------')
        # check wich input parameter is given
        if self.postalcode:
            target_area._target_by_postalcode(self)
            target_input = pd.DataFrame({'typ': 'postalcode',
                                         'data': [self.postalcode],
                                         'power_levels': [self.power_levels],
                                         'gas_levels': [self.gas_levels]})
            self.grid_data.target_input = target_input
        elif self.town_name:
            target_area._target_by_town_name(self)
            target_input = pd.DataFrame({'typ': 'town name',
                                         'data': [self.town_name],
                                         'power_levels': [self.power_levels],
                                         'gas_levels': [self.gas_levels]})
            self.grid_data.target_input = target_input
        elif self.federal_state:
            target_area._target_by_federal_state(self)
            target_input = pd.DataFrame({'typ': 'federal state',
                                         'federal_states': [self.federal_state],
                                         'data': [self.federal_state_postal],
                                         'power_levels': [self.power_levels],
                                         'gas_levels': [self.gas_levels]})
            self.grid_data.target_input = target_input
        elif self.own_area:
            self.target = gpd.read_file(self.own_area)
            if 'id' in self.target.keys():
                self.target = self.target.drop(columns=['id'])
            target_area._own_area_postal(self)
            target_input = pd.DataFrame({'typ': 'own area',
                                         'data': [self.own_postal],
                                         'power_levels': [self.power_levels],
                                         'gas_levels': [self.gas_levels]})
            self.grid_data.target_input = target_input
        else:
            raise SyntaxError('target area wasn`t defined')
        # write area informations into grid_data
        self.grid_data.area = self.grid_data.area.append(self.target)
        self.grid_data.area = self.grid_data.area.set_crs(dave_settings()['crs_main'])
        # check if requested model is already in the archiv
        if not self.grid_data.target_input.iloc[0].typ == 'own area':
            file_exists, file_name = archiv_inventory(self.grid_data, read_only=True)
        else:
            file_exists = False
            file_name = 'None'
        if not file_exists:
            # create borders for target area, load osm-data and write into grid data
            if self.town_name:
                diff_targets = self.target['town'].drop_duplicates()
                for i in range(0, len(diff_targets)):
                    town = self.target[self.target.town == diff_targets.iloc[i]]
                    if len(town) > 1:
                        border = cascaded_union(town.geometry.tolist()).convex_hull
                    else:
                        border = town.iloc[0].geometry.convex_hull
                    # Obtain data from OSM
                    target_area._from_osm(self, target=border, target_town=diff_targets.iloc[i])
            else:
                for i in range(0, len(self.target)):
                    border = self.target.iloc[i].geometry.convex_hull
                    # Obtain data from OSM
                    target_area._from_osm(self, target=border, target_number=i)
            # reset index for all osm data
            self.grid_data.roads.roads = self.grid_data.roads.roads.reset_index(drop=True)
            self.grid_data.roads.roads_plot = self.grid_data.roads.roads_plot.reset_index(drop=True)
            self.grid_data.landuse = self.grid_data.landuse.reset_index(drop=True)
            self.grid_data.buildings.for_living = self.grid_data.buildings.for_living.reset_index(drop=True)
            self.grid_data.buildings.commercial = self.grid_data.buildings.commercial.reset_index(drop=True)
            self.grid_data.buildings.other = self.grid_data.buildings.other.reset_index(drop=True)
            # find road junctions
            target_area.road_junctions(self)
            return file_exists, file_name
        else:
            return file_exists, file_name
