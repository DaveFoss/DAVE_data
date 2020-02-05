import pandapower
import geopandas as gpd
import shapely.geometry
from shapely import affinity
import pandas as pd
import copy



def nearest_road_circle(building_centroids, roads):
    """
    This function finds the shortest way between a building centroid and a road. For this the Method
    uses a circle around the building centroid and raise the radius of the circle until there is a 
    intersection between the circle and the first road. 
    
    INPUT:
        **building centroids** (GeoDataSeries) - buildings in the target area
        **roads** (GeoDataFrame) - relevant roads in the target area
    
    OUTPUT:
        **building connections** (dict) - 
        
    """
    
    
    #return building_connections

def nearest_road_radial(building_centroids, roads, line_length=2E-3, line_ankle=10):
    """
    This function finds the shortest way between a building centroid and a road. For this the Method
    uses radial lines which start from the building centroid. From that there are many 
    intersections between the radial lines and the roads. At the last step the intersection point
    with the shortest distance to the building centroid will be searched
    
    INPUT:
        **building centroids** (GeoDataSeries) - buildings in the target area
        **roads** (GeoDataFrame) - relevant roads in the target area
    
    OPTIONAL:
        **line length** (float, default 2E-3) - defines the length auf the radial lines
        **line amkle** (float, default 10) - defines ankle between the radial lines
    
    OUTPUT:
        **building connections** (DataFrame) - DataFrame includes the shortest connection to a road for each building centroid

        
    """
    # finding nearest connection between the building centroids and the roads
    nearest_points = gpd.GeoSeries([])
    for centroid in building_centroids:
        # create radial lines for searching
        line = shapely.geometry.LineString([(centroid.x,centroid.y),
                                            (centroid.x,centroid.y+line_length)])
        line_rad = [affinity.rotate(line, i, (centroid.x,centroid.y)) for i in range(0,360,line_ankle)]
        multiline_rad = shapely.ops.cascaded_union(line_rad)
        # create multistring of relevant roads and intersect radial lines with it
        multiline_roads = shapely.ops.cascaded_union(roads.geometry)
        points_int = multiline_roads.intersection(multiline_rad)
        if not points_int:
            # if there is no intersection point set it equal the building point
            points_int = centroid
        # finding nearest point
        point_near = shapely.ops.nearest_points(centroid, points_int)[1]
        # write data in  series
        building_index = building_centroids[building_centroids==centroid].index[0]
        nearest_points[building_index]=point_near
    building_connections = pd.concat([building_centroids, nearest_points], axis=1)
    building_connections.columns = ['building centroid', 'nearest point']  
    return building_connections

def create_lv_topology(target_area):
    """
    This function creates a dictonary with all relevant geographical informations for the target area

    INPUT:
        **target area** (dict) - all Informations about the target area

    OPTIONAL:

    OUTPUT:
        **grid data** (dict) - expanded target area dictonary with all informations about the grid
        **grid model** (attrdict) - PANDAPOWER attrdict
    EXAMPLE:
    """
    # search shortest way between building centroid and road for relevant buildings
    buildings_index = list(target_area['buildings']['for_living'].append(target_area['buildings'] \
                           ['commercial']).index)
    centroids = target_area['buildings']['building_centroids'][target_area['buildings'] \
                            ['building_centroids'].index.isin(buildings_index)]
    
    building_connections = nearest_road_radial(building_centroids= centroids,
                                              roads= target_area['roads'])
    grid_data = copy.copy(target_area)
    grid_data['buildings']['building_connections'] = building_connections
    
    """
    Ablauf:
    1. suchen der kürzesten verbindung zwischen einem Gebäudemittelpunkt und einer Straße
    2. Erstellen eines Endpunktes auf der Straße für diese kürzeste Verbindung
    3. pandapower leeres Netz erstellen
    4. Erstellen der relevanten gebäudeknoten und der Endknoten aus der nähesten straße funktion
    5. erstellen einer pandapower Leitung für jede diese verbindungen (Leitung muss dann erstmal standarttyp sein)
    6. Erstellen der weiteren knoten bzw. umspannwerke aus OSM raussuchen
    7. Leitungsinformationen für lv von OSM beziehen
    8. Verbinden der Gebäudestiche miteinander, entlang der Straße
    9. Externes Netz an den Übergabestellen zur mv ebene erstellen
    """
    
    
    return grid_data#, grid_model
   
  

