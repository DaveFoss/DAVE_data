import geopandas as gpd
import geopandas_osm.osm as gpdosm

from dave.datapool import read_postal, read_federal_states


def _from_osm(target, roads=False,roads_plot=False,buildings=False, landuse=False):
    """
    This function searches for data on OSM and filters the relevant paramerters for grid modeling
    """
    if roads:
        roads=gpdosm.query_osm('way', target, recurse='down', 
                               tags=['highway~"tertiary|unclassified|residential"'])
        # define road parameters which are relevant for the grid modeling
        relevant_columns=['geometry',
                          'name']
        roads= roads.filter(relevant_columns)
        #consider only the linestring elements
        roads = roads[roads.geometry.length != 0]
        return roads
    
    if roads_plot:
        roads_plot=gpdosm.query_osm('way', target, recurse='down', 
                                    tags=['highway~"motorway|trunk|primary|secondary"'])
        # define road parameters which are relevant for the grid modeling
        relevant_columns=['geometry',
                          'name']
        roads_plot= roads_plot.filter(relevant_columns)
        #consider only the linestring elements
        roads_plot = roads_plot[roads_plot.geometry.length != 0]
        return roads_plot
    
    if buildings: 
        buildings=gpdosm.query_osm('way', target, recurse='down', tags=['building'])
        # define building parameters which are relevant for the grid modeling
        relevant_columns=['addr:housenumber',
                          'addr:street',
                          'addr:suburb',
                          'amenity',
                          'building',
                          'building:levels',
                          'geometry',
                          'name']
        buildings= buildings.filter(relevant_columns)
        #consider only the linestring elements
        buildings=buildings[buildings.geometry.length != 0]
        # create building centroid and categorize buildings
        for_living=['apartments',
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
        commercial=['commercial',
                    'hall',
                    'industrial',
                    'kindergarten',
                    'kiosk',
                    'office',
                    'retail',
                    'school',
                    'supermarket',
                    'warehouse']
        buildings={'for_living':buildings[buildings.building.isin(for_living)],
                   'commercial':buildings[buildings.building.isin(commercial)],
                   'other':buildings[~buildings.building.isin(for_living+commercial)],
                   'building_centroids': buildings.centroid}
        buildings['building_centroids'].rename('centroid')
        return buildings
    if landuse:
        landuse=gpdosm.query_osm('way', target, recurse='down', tags=['landuse'])
        relevant_columns=['industrial',
                          'landuse',
                          'geometry',
                          'name']
        landuse= landuse.filter(relevant_columns)
        #consider only the linestring elements
        landuse=landuse[landuse.geometry.length != 0]
        return landuse
    
def _target_by_postalcode(postalcode):
    """
    This function filter the postalcode informations for the target area. 
    Multiple postalcode areas will be combinated
    """
    postal = read_postal()
    for i in range(len(postalcode)):
        if i==0:
            target=postal[postal.postalcode==postalcode[i]]
        else:
            target=target.append(postal[postal.postalcode==postalcode[i]])
    return target

def _target_by_town_name(town_name):
    """
    This function filter the postalcode informations for the target area. 
    Multiple town name areas will be combinated
    """
    postal = read_postal()
    for i in range(len(town_name)):
        if i==0: 
            target=postal[postal.town==town_name[0].capitalize()]
        else:
            target=target.append(postal[postal.town==town_name[i].capitalize()])
        if target.empty:
            raise ValueError('town name wasn`t found. Please check your input' )
    return target

def _target_by_federal_state(federal_state):
    """
    This function filter the federal state informations for the target area. 
    Multiple federal state areas will be combinated
    """
    states = read_federal_states()
    for i in range(len(federal_state)):
        # bring name in right form
        state_name = federal_state[i].split('-')
        if len(state_name)==1:
            state_name = state_name[0].capitalize()
        else:
            state_name = state_name[0].capitalize()+'-'+state_name[1].capitalize()
        if i==0:             
            target=states[states['name']==state_name]
        else:
            target=target.append(states[states['name']==state_name])
        if target.empty:
            raise ValueError('federal state name wasn`t found. Please check your input' )
    return target
    
def target_area(postalcode=None, town_name=None, federal_state=None, own_area=None, buffer=1E-2,
                roads=True, roads_plot=True, buildings=True, landuse=True):
    """
    This function creates a dictonary with all relevant geographical informations for the target area

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

    OUTPUT:
        **target area** (dict) - all relevant informations for the target area

    EXAMPLE:
        from dave.topology import target_area
        kassel = target_area(town_name = ['Kassel'])
    """
    # check wich input parameter is given
    if postalcode:
        target=_target_by_postalcode(postalcode)
    elif town_name:
        target=_target_by_town_name(town_name)
    elif federal_state:
        target=_target_by_federal_state(federal_state)
    elif own_area:
        target=gpd.read_file(own_area)
    else:
        raise SyntaxError('target area wasn`t defined')
    # combine polygons and transfer into a shaply format
    border=target.geometry.cascaded_union.buffer(buffer)
    # Obtain data from OSM
    roads=_from_osm(target=border, roads=roads) if roads else []
    roads_plot=_from_osm(target=border, roads_plot=roads_plot) if roads_plot else []
    buildings=_from_osm(target=border, buildings=buildings) if buildings else []
    landuse=_from_osm(target=border, landuse=landuse) if landuse else []
    # write all data into a dictonary
    target_area = {'area':target,
                   'roads':roads, 
                   'roads_plot':roads_plot,
                   'buildings':buildings,
                   'landuse':landuse}
    return target_area   
    

    
    



"""
Hier muss mit rein:
 - Häuser, Straße und was sonst noch relevant von osm ist 

"""