import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd


def plot_land(area, only_area=False):
    """
    This funcition plots the polygon of the target area, which can be used for the background.

    INPUT:
    **area** (GeoDataFrame) - polygon of the target area

    OUTPUT:
        **ax** - axes of figure
    """
    if only_area:
        fig = plt.figure(frameon=False, figsize=(18, 12))
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')
        area.plot(color='k', alpha=0.1, ax=ax)
    else:
        fig = plt.figure(frameon=False, figsize=(18, 12))
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')
        ax = area.plot(color='k', alpha=0.1, ax=ax)
        ax.margins(0)
        return ax


def plot_target_area(target_area):
    """
    This function plots the geographical informations in the target area

    INPUT:
        **target area** (dict) - all Informations about the target area

    OUTPUT:

    EXAMPLE:
    """
    # input data
    roads_plot = target_area['roads']['roads_plot']
    roads = target_area['roads']['roads']
    road_junctions = target_area['roads']['road_junctions']
    buildings = target_area['buildings']
    if isinstance(buildings, pd.DataFrame) and not buildings.empty:
        buildings_for_living = target_area['buildings']['for_living']
        buildings_commercial = target_area['buildings']['commercial']
        buildings_other = target_area['buildings']['other']
        building_centroids = target_area['buildings']['building_centroids']
    # check if there is any data in target area otherwise plot only the area
    if isinstance(buildings, pd.DataFrame):
        data = [roads_plot, roads, road_junctions, buildings]
        data_check = pd.concat(data)
        if data_check.empty:
            data_empty = True
        else:
            data_empty = False
    else:
        data_empty = False
    if data_empty:
        # plot target area
        plot_land(target_area['area'], only_area = True)
    else:
        # plot target area
        ax = plot_land(target_area['area'])
        # plot road informations
        if not roads_plot.empty:
            # these highways are only relevant for plotting
            target_area['roads']['roads_plot'].plot(ax=ax, color='k')  
        if not roads.empty:
            roads.plot(ax=ax, color='k')
        if not road_junctions.empty:
            road_junctions.plot(ax=ax, color='r')
        # plot buildings
        if isinstance(buildings, pd.DataFrame) and not buildings.empty:
            if not buildings_for_living.empty:
                buildings_for_living.plot(ax=ax, color='g')
            if not buildings_commercial.empty:
                buildings_commercial.plot(ax=ax, color='b')
            if not buildings_other.empty:
                buildings_other.plot(ax=ax, color='k')
            # plot building centroids
            if not building_centroids.empty:
                building_centroids.plot(ax=ax, color='m', markersize=1)


def plot_grid_data(grid_data):
    """
    This function plots the geographical informations in the target area with the grid data

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:

    EXAMPLE:
    """
    roads_plot = grid_data['roads']['roads_plot']
    roads = grid_data['roads']['roads']
    road_junctions = grid_data['roads']['road_junctions']
    line_buildings = grid_data['lines_lv']['line_buildings']
    line_connections = grid_data['lines_lv']['line_connections']
    renewable_plants = grid_data['components']['renewable_powerplants']
    conventional_plants = grid_data['components']['conventional_powerplants']
    buildings = grid_data['buildings']
    if isinstance(buildings, pd.DataFrame) and not buildings.empty:
        buildings_for_living = grid_data['buildings']['for_living']
        buildings_commercial = grid_data['buildings']['commercial']
        buildings_other = grid_data['buildings']['other']
        building_centroids = grid_data['buildings']['building_connections']['building_centroid']
        building_nearest = grid_data['buildings']['building_connections']['nearest_point']
    # check if there is any data in target area otherwise plot only the area
    if isinstance(buildings, pd.DataFrame):
        data = [roads_plot, roads, road_junctions, line_buildings, 
                line_connections, renewable_plants, conventional_plants, buildings]
        data_check = pd.concat(data)
        if data_check.empty:
            data_empty = True
        else:
            data_empty = False
    else:
        data_empty = False
    if data_empty:
        # plot target area
        plot_land(grid_data['area'], only_area = True) 
    else:
        # plot target area
        ax = plot_land(grid_data['area'])
        # plot informations
        if not roads_plot.empty:
            roads_plot.plot(ax=ax, color='k', alpha=0.2)  
        if not roads.empty:
            roads.plot(ax=ax, color='k', alpha=0.2)
        #if ~road_junctions.empty:
        #    road_junctions.plot(ax=ax, color='r')
        # plot buildings
        if isinstance(buildings, pd.DataFrame) and not buildings.empty:
            if not buildings_for_living.empty:
                buildings_for_living.plot(ax=ax, color='k', alpha=0.2)
            if not buildings_commercial.empty:
                buildings_commercial.plot(ax=ax, color='k', alpha=0.2)
            if not buildings_other.empty:
                buildings_other.plot(ax=ax, color='k', alpha=0.2)
        # plot building connections (points and lines) and line connetions
            if not building_centroids.empty:
                centroids = gpd.GeoSeries(list(building_centroids))
                centroids.plot(ax=ax, color='b', markersize=1)
            if not building_nearest.empty:
                nearest_point = gpd.GeoSeries(list(building_nearest))
                nearest_point.plot(ax=ax, color='b', markersize=5)
        if not line_buildings.empty:
            line_buildings.plot(ax=ax, color='b')
        if not line_connections.empty:
            line_connections.plot(ax=ax, color='b')
        # plot electrical components
        if not renewable_plants.empty:
            renewable_plants.plot(ax=ax, color='g')
        if not conventional_plants.empty:
            conventional_plants.plot(ax=ax, color='m')
        
    # hier dann noch alle weiteren komponenten die erstellt wurden mit rein und für die 
    # verschiedenen Spannungs und Druck ebenen.


def plot_pandapower():
    # hier die gewünschte pandapower plotting funktion rein schreiben 
    pass


def plot_pandapipes():
    # hier die gewünschte pandapipes plotting funktion rein schreiben 
    pass
