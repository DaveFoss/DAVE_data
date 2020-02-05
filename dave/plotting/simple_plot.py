import matplotlib.pyplot as plt

def plot_land(area):
    """
    This funcition plots the polygon of the target area, which can be used for the background.
    
    INPUT:
    **area** (GeoDataFrame) - polygon of the target area
    
    OUTPUT:
        **ax** - axes of figure
    """
    fig = plt.figure(frameon=False, figsize=(18,12))
    ax = fig.add_subplot(1, 1, 1)
    ax.axis('off')
    ax=area.plot(color='k', alpha=0.1, ax=ax)
    ax.margins(0)
    return ax

def simple_plot(target_area):
    """
    This function creates a dictonary with all relevant geographical informations for the target area

    INPUT:
        **target area** (dict) - all Informations about the target area

    OUTPUT:

    EXAMPLE:
    """
    # plot target area
    ax = plot_land(target_area['area'])
    # plot highways
    if ~target_area['roads_plot'].empty:
        target_area['roads_plot'].plot(ax=ax, color='k') # these highways are only relevant for plotting
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





