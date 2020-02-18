import matplotlib.pyplot as plt
import geopandas as gpd


def plot_land(area):
    """
    This funcition plots the polygon of the target area, which can be used for the background.

    INPUT:
    **area** (GeoDataFrame) - polygon of the target area

    OUTPUT:
        **ax** - axes of figure
    """
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
    # plot target area
    ax = plot_land(target_area['area'])
    # plot highways
    if ~target_area['roads_plot'].empty:
        target_area['roads_plot'].plot(ax=ax, color='k')  # these highways are only relevant for plotting
    if ~target_area['roads'].empty:
        target_area['roads'].plot(ax=ax, color='k')
    # plot buildings
    if ~target_area['buildings']['for_living'].empty:
        target_area['buildings']['for_living'].plot(ax=ax, color='g')
    if ~target_area['buildings']['commercial'].empty:
        target_area['buildings']['commercial'].plot(ax=ax, color='b')
    if ~target_area['buildings']['other'].empty:
        target_area['buildings']['other'].plot(ax=ax, color='k')
    # plot building centroids
    if ~target_area['buildings']['building_centroids'].empty:
        target_area['buildings']['building_centroids'].plot(ax=ax, color='r', markersize=1)


def plot_grid_data(grid_data):
    """
    This function plots the geographical informations in the target area with the grid data

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:

    EXAMPLE:
    """
    # plot target area
    ax = plot_land(grid_data['area'])
    # plot highways
    if ~grid_data['roads_plot'].empty:
        grid_data['roads_plot'].plot(ax=ax, color='k', alpha=0.2)  
    if ~grid_data['roads'].empty:
        grid_data['roads'].plot(ax=ax, color='k', alpha=0.2)
    # plot buildings
    if ~grid_data['buildings']['for_living'].empty:
        grid_data['buildings']['for_living'].plot(ax=ax, color='k', alpha=0.2)
    if ~grid_data['buildings']['commercial'].empty:
        grid_data['buildings']['commercial'].plot(ax=ax, color='k', alpha=0.2)
    if ~grid_data['buildings']['other'].empty:
        grid_data['buildings']['other'].plot(ax=ax, color='k', alpha=0.2)
    # plot building connections (points and lines)
    if ~grid_data['buildings']['building_connections']['building_centroid'].empty:
        centroids = gpd.GeoSeries(list(
                grid_data['buildings']['building_connections']['building_centroid']))
        centroids.plot(ax=ax, color='b', markersize=1)
    if ~grid_data['buildings']['building_connections']['nearest_point'].empty:
        nearest_point = gpd.GeoSeries(list(
                grid_data['buildings']['building_connections']['nearest_point']))
        nearest_point.plot(ax=ax, color='b', markersize=1)
    if ~grid_data['lines_lv'].empty:
        grid_data['lines_lv'].plot(ax=ax, color='b')
    
    # hier dann noch alle weiteren komponenten die erstellt wurden mit rein und für die 
    # verschiedenen Spannungs und Druck ebenen. 


def plot_pandapower():
    # hier die gewünschte pandapower plotting funktion rein schreiben 
    pass


def plot_pandapipes():
    # hier die gewünschte pandapipes plotting funktion rein schreiben 
    pass
