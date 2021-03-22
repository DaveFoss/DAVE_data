import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import pandas as pd
import contextily as ctx

from dave import dave_output_dir


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
        fig = plt.figure(frameon=False, figsize=(50, 50))
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')
        ax = area.plot(color='k', alpha=0.1, ax=ax)
        ax.margins(0)
        return ax


def plot_target_area(grid_data):
    """
    This function plots the geographical informations in the target area

    INPUT:
        **grid_data** (attrdict) - all Informations about the target area

    OUTPUT:
        **target area plot** (svg file) - plot as vektor graphic
    """
    # input data
    roads_plot = grid_data.roads.roads_plot
    roads = grid_data.roads.roads
    road_junctions = grid_data.roads.road_junctions
    buildings_for_living = grid_data.buildings.for_living
    buildings_commercial = grid_data.buildings.commercial
    buildings_other = grid_data.buildings.other
    buildings_all = pd.concat([buildings_for_living, buildings_commercial, buildings_other])
    if not buildings_all.empty:
        building_centroids = buildings_all.centroid
    else:
        building_centroids = gpd.GeoSeries([])
    # check if there is any data in target area, otherwise plot only the area
    data = [roads_plot,
            roads,
            road_junctions,
            buildings_for_living,
            buildings_commercial,
            buildings_other,
            building_centroids]
    data_check = pd.concat(data)
    if data_check.empty:
        # plot target area
        plot_land(grid_data['area'], only_area=True)
    else:
        # plot target area
        ax = plot_land(grid_data['area'])
        # plot road informations
        if not roads_plot.empty:
            # these highways are only relevant for plotting
            roads_plot.plot(ax=ax, color='k', label='Roads')
        if not roads.empty:
            roads.plot(ax=ax, color='k')
        if not road_junctions.empty:
            road_junctions.plot(ax=ax, color='r', label='Road junctions')
        # plot buildings
        if not buildings_for_living.empty:
            buildings_for_living.plot(ax=ax, color='g', label='Living Buildings')
        if not buildings_commercial.empty:
            buildings_commercial.plot(ax=ax, color='b', label='Commercial Buildings')
        if not buildings_other.empty:
            buildings_other.plot(ax=ax, color='k', label='Other Buildings')
        # plot building centroids
        if not building_centroids.empty:
            building_centroids.plot(ax=ax, color='m', markersize=1, label='Building Centroids')
        # legende
        ax.legend()
        # titel
        plt.title('Target Area')
        # save plot in the dave output folder
        file_path = dave_output_dir + '\\target_area.svg'
        plt.savefig(file_path, dpi=300)


def plot_grid_data(grid_data):
    """
    This function plots primary the grid data and auxillary greyed out the
    geographical informations in the target area

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:
        **grid data plot** (svg file) - plot as vektor graphic
    """
    roads_plot = grid_data.roads.roads_plot
    roads = grid_data.roads.roads
    road_junctions = grid_data.roads.road_junctions
    lv_lines = grid_data.lv_data.lv_lines
    lv_nodes = grid_data.lv_data.lv_nodes
    mv_lines = grid_data.mv_data.mv_lines
    mv_nodes = grid_data.mv_data.mv_nodes
    ehv_nodes = grid_data.ehv_data.ehv_nodes
    ehv_lines = grid_data.ehv_data.ehv_lines
    hv_nodes = grid_data.hv_data.hv_nodes
    hv_lines = grid_data.hv_data.hv_lines
    hp_junctions = grid_data.hp_data.hp_junctions
    hp_pipes = grid_data.hp_data.hp_pipes
    renewable_plants = grid_data.components_power.renewable_powerplants
    conventional_plants = grid_data.components_power.conventional_powerplants
    buildings_for_living = grid_data.buildings.for_living
    buildings_commercial = grid_data.buildings.commercial
    buildings_other = grid_data.buildings.other
    substations = pd.concat([grid_data.components_power.substations.ehv_hv,
                             grid_data.components_power.substations.hv_mv])
    # check if there is any data in target area otherwise plot only the area
    data = [roads_plot,
            roads,
            road_junctions,
            buildings_for_living,
            buildings_commercial,
            buildings_other,
            substations,
            lv_nodes,
            lv_lines,
            mv_lines,
            mv_nodes,
            renewable_plants,
            conventional_plants,
            ehv_nodes,
            ehv_lines,
            hv_nodes,
            hv_lines,
            hp_junctions,
            hp_pipes]
    data_check = pd.concat(data)
    if data_check.empty:
        # plot target area
        plot_land(grid_data['area'], only_area=True)
    else:
        # plot target area
        ax = plot_land(grid_data['area'])
        # plot road informations
        if not roads_plot.empty:
            roads_plot.plot(ax=ax, color='k', alpha=0.2)
        if not roads.empty:
            roads.plot(ax=ax, color='k', alpha=0.2)
        # plot buildings
        if not buildings_for_living.empty:
            buildings_for_living.plot(ax=ax, color='k', alpha=0.2)
        if not buildings_commercial.empty:
            buildings_commercial.plot(ax=ax, color='k', alpha=0.2)
        if not buildings_other.empty:
            buildings_other.plot(ax=ax, color='k', alpha=0.2)
        # plot lv topology
        if not lv_nodes.empty:
            lv_nodes.plot(ax=ax, color='b', label='LV Nodes')
        if not lv_lines.empty:
            lv_lines.plot(ax=ax, color='b', label='LV Lines')
        # plot mv topology
        if not mv_nodes.empty:
            mv_nodes.plot(ax=ax, color='m', markersize=6, label='MV Nodes')
        if not mv_lines.empty:
            mv_lines.plot(ax=ax, color='m', label='MV Lines')
        """
        # plot electrical components
        if not renewable_plants.empty:
            renewable_plants.plot(ax=ax, color='g',label='renewable power plants')
        if not conventional_plants.empty:
            conventional_plants.plot(ax=ax, color='m',label='conventional power plants')
        """
        # plot ehv topology
        if not ehv_nodes.empty:
            ehv_nodes.plot(ax=ax, color='k', markersize=6, label='EHV Nodes')
        if not ehv_lines.empty:
            ehv_lines_380 = ehv_lines[ehv_lines.voltage_kv == 380]
            if not ehv_lines_380.empty:
                ehv_lines_380.plot(ax=ax, color='r', zorder=3, label='380 kV Lines')
            ehv_lines_220 = ehv_lines[ehv_lines.voltage_kv == 220]
            if not ehv_lines_220.empty:
                ehv_lines_220.plot(ax=ax, color='b', zorder=2, label='220 kV Lines')
        # plot hv topology
        if not hv_nodes.empty:
            hv_nodes.plot(ax=ax, color='g', markersize=6, label='HV Nodes')
        if not hv_lines.empty:
            hv_lines.plot(ax=ax, color='g', markersize=6, label='HV Lines')
        # plot hp topology
        if not hp_junctions.empty:
            hp_junctions.plot(ax=ax, color='k', markersize=6, label='HP Junctions')
        if not hp_pipes.empty:
            hp_pipes.plot(ax=ax, color='k', zorder=1, label='HP Pipes')
        # plot substations
        if not substations.empty:
            substations.plot(ax=ax, color='k', alpha=0.2, label='EHV Substations')
        # legende
        ax.legend()
        # titel
        plt.title('Grid Data')
        # save plot in the dave output folder
        file_path = dave_output_dir + '\\grid_data.svg'
        plt.savefig(file_path, dpi=300)
    # hier dann noch alle weiteren komponenten die erstellt wurden mit rein und für die
    # verschiedenen Spannungs und Druck ebenen.


def plot_grid_data_osm(grid_data):
    """
    This function plots primary the grid data with a osm map in the background

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:
        **grid data osm plot** (svg file) - plot as vektor graphic
    """
    lv_nodes = grid_data.lv_data.lv_nodes
    lv_lines = grid_data.lv_data.lv_lines
    ehv_nodes = grid_data.ehv_data.ehv_nodes
    ehv_substations = grid_data.ehv_data.ehv_substations
    ehv_lines = grid_data.ehv_data.ehv_lines
    hv_nodes = grid_data.hv_data.hv_nodes
    hv_lines = grid_data.hv_data.hv_lines
    renewable_plants = grid_data.components_power.renewable_powerplants
    conventional_plants = grid_data.components_power.conventional_powerplants
    # check if there is any data in target area otherwise plot only the area
    data = [lv_nodes,
            lv_lines,
            renewable_plants,
            conventional_plants,
            ehv_nodes,
            ehv_substations,
            ehv_lines,
            hv_nodes,
            hv_lines]
    data_check = pd.concat(data)
    if data_check.empty:
        # plot target area
        plot_land(grid_data['area'], only_area=True)
    else:
        # plot target area
        test = grid_data['area'].to_crs(epsg=3857)
        ax = plot_land(test)
        # ax = plot_land(grid_data['area'])
        # plot lv topology
        if not lv_nodes.empty:
            lv_nodes = lv_nodes.to_crs(epsg=3857)
            lv_nodes.plot(ax=ax, color='b', label='LV Nodes')
        if not lv_lines.empty:
            lv_lines = lv_lines.to_crs(epsg=3857)
            lv_lines.plot(ax=ax, color='b', label='LV lines')
        # plot electrical components
        if not renewable_plants.empty:
            renewable_plants.plot(ax=ax, color='g')
        if not conventional_plants.empty:
            conventional_plants.plot(ax=ax, color='m')
        # plot ehv topology
        if not ehv_nodes.empty:
            ehv_nodes = ehv_nodes.to_crs(epsg=3857)
            ehv_nodes.plot(ax=ax, color='k', markersize=6, label='EHV Nodes')
        if not ehv_substations.empty:
            ehv_substations = ehv_substations.to_crs(epsg=3857)
            ehv_substations.plot(ax=ax, color='k', alpha=0.2, label='EHV Substations')
        if not ehv_lines.empty:
            ehv_lines_380 = ehv_lines[ehv_lines.voltage_kv == 380]
            if not ehv_lines_380.empty:
                ehv_lines_380 = ehv_lines_380.to_crs(epsg=3857)
                ehv_lines_380.plot(ax=ax, color='red', zorder=3, label='380 kV lines')
            ehv_lines_220 = ehv_lines[ehv_lines.voltage_kv == 220]
            if not ehv_lines_220.empty:
                ehv_lines_220 = ehv_lines_220.to_crs(epsg=3857)
                ehv_lines_220.plot(ax=ax, color='blue', zorder=2, label='220 kV lines')
        # plot hv topology
        if not hv_nodes.empty:
            hv_nodes = hv_nodes.to_crs(epsg=3857)
            hv_nodes.plot(ax=ax, color='k', markersize=6, label='HV Nodes')
        if not hv_lines.empty:
            hv_lines = hv_lines.to_crs(epsg=3857)
            hv_lines.plot(ax=ax, color='green', zorder=1, label='110 kV lines')
        # legende
        ax.legend()
        # titel
        plt.title('Grid Data OSM')
        # plot background osm
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        # ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite)  # stamen design
        # save plot in the dave output folder
        file_path = dave_output_dir + '\\grid_data.svg'
        plt.savefig(file_path, format='svg', dpi=300)


def plot_landuse(grid_data):
    """
    This function plots the landuses in the target area

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:
        **landuse plot** (svg file) - plot as vektor graphic
    """
    if not grid_data.landuse.empty:
        landuse_residential = grid_data.landuse[grid_data.landuse.landuse == 'residential']
        landuse_industrial = grid_data.landuse[grid_data.landuse.landuse == 'industrial']
        landuse_commercial = grid_data.landuse[grid_data.landuse.landuse.isin(['commercial',
                                                                               'retail'])]
        # plot target area
        ax = plot_land(grid_data['area'])
        # plot landuses
        plot_patch = []
        if not landuse_residential.empty:
            landuse_residential.plot(ax=ax, color='b')
            blue_patch = mpatches.Patch(color='b', label='Residential')
            plot_patch.append(blue_patch)
        if not landuse_industrial.empty:
            landuse_industrial.plot(ax=ax, color='r', label='Industrial')
            red_patch = mpatches.Patch(color='r', label='Industrial')
            plot_patch.append(red_patch)
        if not landuse_commercial.empty:
            landuse_commercial.plot(ax=ax, color='g', label='Commercial')
            green_patch = mpatches.Patch(color='g', label='Commercial')
            plot_patch.append(green_patch)
        # legende
        plt.legend(handles=plot_patch)
        # titel
        plt.title('Landuse')
        # save plot in the dave output folder
        file_path = dave_output_dir + '\\landuse.svg'
        plt.savefig(file_path, dpi=300)


def plot_generator():
    """
    This function plots the power plants in the target area

    INPUT:
        **grid_data** (dict) - all Informations about the target area and the grid

    OUTPUT:
        **generator plot** (svg file) - plot as vektor graphic
    """
    # hier eine Plotting funktion die nur die Erzeuger im Zielgebiet aufzeigt und
    # verschiedene Farben für die verschiedenen Energieträger
    pass
