import geopandas as gpd
import geopandas_osm.osm as gpdosm
from shapely.ops import cascaded_union

from dave.datapool import read_postal, read_federal_states


class target_area():
    """
    This class contains functions to define a target area and getting all relevant osm data for it

    INPUT:
        One of these parameters must be set:
        **postalcode** (List of strings) - numbers of the target postalcode areas
        **town_name** (List of strings) - names of the target towns
        **federal_state** (List of strings) - names of the target federal states
        **own_area** (string) - full path to a shape file which includes own target area (e.g. "C:/Users/name/test/test.shp")

    OPTIONAL:
        **buffer** (float, default 1E-2) - buffer for the target area
        **roads** (boolean, default True) - obtain informations about roads which are relevant for the grid model
        **roads_plot** (boolean, default False) - obtain informations about roads which can be nice for the visualization
        **buildings** (boolean, default True) - obtain informations about buildings in the target area
        **landuse** (boolean, default True) - obtain informations about the landuse of the target area
    """
    def __init__(self, postalcode=None, town_name=None, federal_state=None, own_area=None,
                 buffer=1E-2, roads=True, roads_plot=True, buildings=True, landuse=True):
        # Init input parameters
        self.postalcode = postalcode
        self.town_name = town_name
        self.federal_state = federal_state
        self.own_area = own_area
        self.buffer = buffer
        self.roads = roads
        self.roads_plot = roads_plot
        self.buildings = buildings
        self.landuse = landuse

    def _from_osm(self, target, target_number=None, target_town=None):
        """
        This function searches for data on OpenStreetMap (OSM) and filters the relevant paramerters
        for grid modeling
        """
        # search relevant road informations in the target area
        if self.roads:
            roads = gpdosm.query_osm('way', target, recurse='down',
                                     tags=['highway~"tertiary|unclassified|residential|living_street|footway"'])
            # define road parameters which are relevant for the grid modeling
            relevant_columns = ['geometry',
                                'name',
                                'highway']
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
        else:
            roads = []
        # search irrelevant road informations in the target area for a better overview
        if self.roads_plot:
            roads_plot = gpdosm.query_osm('way', target, recurse='down',
                                          tags=['highway~"motorway|trunk|primary|secondary"'])
            # define road parameters which are relevant for the grid modeling
            relevant_columns = ['geometry',
                                'name']
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
        else:
            roads_plot = []
        # search building informations in the target area
        if self.buildings:
            buildings = gpdosm.query_osm('way', target, recurse='down', tags=['building'])
            # define building parameters which are relevant for the grid modeling
            relevant_columns = ['addr:housenumber',
                                'addr:street',
                                'addr:suburb',
                                'amenity',
                                'building',
                                'building:levels',
                                'geometry',
                                'name']
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
            # create building centroid and categorize buildings
            for_living = ['apartments',
                          'detached',
                          'dormitory',
                          'farm',
                          'house',
                          'houseboat',
                          'residential',
                          'semidetached_house',
                          'static_caravan',
                          'terrace',
                          'yes']
            commercial = ['commercial',
                          'hall',
                          'industrial',
                          'kindergarten',
                          'kiosk',
                          'office',
                          'retail',
                          'school',
                          'supermarket',
                          'warehouse']
            buildings = {'for_living': buildings[buildings.building.isin(for_living)],
                         'commercial': buildings[buildings.building.isin(commercial)],
                         'other': buildings[~buildings.building.isin(for_living+commercial)],
                         'building_centroids': buildings.centroid}
            buildings['building_centroids'].rename('centroid')
        else:
            buildings = []
        # search landuse informations in the target area
        if self.landuse:
            landuse = gpdosm.query_osm('way', target, recurse='down', tags=['landuse'])
            relevant_columns = ['industrial',
                                'landuse',
                                'geometry',
                                'name']
            landuse = landuse.filter(relevant_columns)
            # consider only the linestring elements
            landuse = landuse[landuse.geometry.length != 0]
            # consider only landuses which intersects the target area
            if target_number or target_number == 0:
                target_area = self.target.geometry.iloc[target_number]
            elif target_town:
                targets = self.target[self.target.town == target_town]
                target_area = cascaded_union(targets.geometry.tolist())
            landuse = landuse[landuse.geometry.intersects(target_area)]
        else:
            landuse = []
        # create Dictonary with road informations
        roads = {'roads': roads,
                 'roads_plot': roads_plot}
        # create dictonary with all informations for this target area
        self.target_area = {'area': self.target,
                            'roads': roads,
                            'buildings': buildings,
                            'landuse': landuse}

    def road_junctions(self, roads):
        """
        This function searches junctions for the relevant roads in the target area
        """
        junction_points = []
        for i, line in roads.iterrows():
            # create multipolygon for lines without the one under consideration
            other_lines = roads.drop([i])
            other_lines = cascaded_union(other_lines.geometry)
            # find line intersections
            junctions = line.geometry.intersection(other_lines)
            if junctions.geom_type == 'Point':
                junction_points.append(junctions)
            elif junctions.geom_type == 'MultiPoint':
                for point in junctions:
                    junction_points.append(point)
        # delet duplicates
        junction_points = gpd.GeoSeries(junction_points)
        self.road_junctions = junction_points.drop_duplicates()  #[junction_points.duplicated()]

    def _target_by_postalcode(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple postalcode areas will be combinated
        """
        postal = read_postal()
        for i in range(len(self.postalcode)):
            if i == 0:
                target = postal[postal.postalcode == self.postalcode[i]]
            else:
                target = target.append(postal[postal.postalcode == self.postalcode[i]])
        self.target = target

    def _target_by_town_name(self):
        """
        This function filter the postalcode informations for the target area.
        Multiple town name areas will be combinated
        """
        postal = read_postal()
        for i in range(len(self.town_name)):
            if i == 0:
                target = postal[postal.town == self.town_name[0].capitalize()]
            else:
                target = target.append(postal[postal.town == self.town_name[i].capitalize()])
            if target.empty:
                raise ValueError('town name wasn`t found. Please check your input')
        self.target = target

    def _target_by_federal_state(self):
        """
        This function filter the federal state informations for the target area.
        Multiple federal state areas will be combinated
        """
        states = read_federal_states()
        for i in range(len(self.federal_state)):
            # bring name in right form
            state_name = self.federal_state[i].split('-')
            if len(state_name) == 1:
                state_name = state_name[0].capitalize()
            else:
                state_name = state_name[0].capitalize()+'-'+state_name[1].capitalize()
            if i == 0:
                target = states[states['name'] == state_name]
            else:
                target = target.append(states[states['name'] == state_name])
            if target.empty:
                raise ValueError('federal state name wasn`t found. Please check your input')
        self.target = target

    def target(self):
        """
        This function creates a dictonary with all relevant geographical informations for the
        target area

        OPTIONAL:
            **buffer** (float, default 1E-2) - buffer for the target area
            **roads** (boolean, default True) - obtain informations about roads which are relevant
                                                for the grid model
            **roads_plot** (boolean, default False) - obtain informations about roads which can be
                                                      nice for the visualization
            **buildings** (boolean, default True) - obtain informations about buildings in the
                                                    target area
            **landuse** (boolean, default True) - obtain informations about the landuse of the
                                                  target area

        OUTPUT:
            **target area** (dict) - all relevant informations for the target area

        EXAMPLE:
            from dave.topology import target_area
            kassel = target_area(town_name = ['Kassel'], buffer=0).target()
        """

        # check wich input parameter is given
        if self.postalcode:
            target_area._target_by_postalcode(self)
        elif self.town_name:
            target_area._target_by_town_name(self)
        elif self.federal_state:
            target_area._target_by_federal_state(self)
        elif self.own_area:
            self.target = gpd.read_file(self.own_area)
        else:
            raise SyntaxError('target area wasn`t defined')

        # create dictonary with all data for the target area(s) from OSM
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
                if i == 0:
                    full_target_area = self.target_area
                else:
                    full_target_area['buildings']['building_centroids'] = full_target_area['buildings']\
                    ['building_centroids'].append(self.target_area['buildings']['building_centroids'])
                    full_target_area['buildings']['commercial'] = full_target_area['buildings']\
                    ['commercial'].append(self.target_area['buildings']['commercial'])
                    full_target_area['buildings']['for_living'] = full_target_area['buildings']\
                    ['for_living'].append(self.target_area['buildings']['for_living'])
                    full_target_area['buildings']['other'] = full_target_area['buildings']\
                    ['other'].append(self.target_area['buildings']['other'])
                    full_target_area['landuse'] = full_target_area['landuse'].append(
                            self.target_area['landuse'])
                    full_target_area['roads']['roads'] = full_target_area['roads']['roads'].append(
                            self.target_area['roads']['roads'])
                    full_target_area['roads']['roads_plot'] = full_target_area['roads'][
                            'roads_plot'].append(self.target_area['roads']['roads_plot'])
        else:
            for i in range(0, len(self.target)):
                border = self.target.iloc[i].geometry.convex_hull
                # Obtain data from OSM
                target_area._from_osm(self, target=border, target_number=i)
                if i == 0:
                    full_target_area = self.target_area
                else:
                    full_target_area['buildings']['building_centroids'] = full_target_area['buildings']\
                    ['building_centroids'].append(self.target_area['buildings']['building_centroids'])
                    full_target_area['buildings']['commercial'] = full_target_area['buildings']\
                    ['commercial'].append(self.target_area['buildings']['commercial'])
                    full_target_area['buildings']['for_living'] = full_target_area['buildings']\
                    ['for_living'].append(self.target_area['buildings']['for_living'])
                    full_target_area['buildings']['other'] = full_target_area['buildings']
                    ['other'].append(self.target_area['buildings']['other'])
                    full_target_area['landuse'] = full_target_area['landuse'].append(
                            self.target_area['landuse'])
                    full_target_area['roads']['roads'] = full_target_area['roads']['roads'].append(
                            self.target_area['roads']['roads'])
                    full_target_area['roads']['roads_plot'] = full_target_area['roads'][
                            'roads_plot'].append(self.target_area['roads']['roads_plot'])
        # find road junctions
        target_area.road_junctions(self, full_target_area['roads']['roads'])
        full_target_area['roads']['road_junctions'] = self.road_junctions
        return full_target_area
