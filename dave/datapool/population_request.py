import geopandas as gpd
import pandas as pd
import rasterio
import rasterio.mask
import tqdm

from dave.settings import dave_settings
from dave.toolbox import get_data_path, intersection_with_area


def request_population(grid_data, output_folder, api_use):
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create population      :           ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    ### get population in raster format
    # get the boundary of area of interest
    boundary = grid_data.area.geometry.unary_union
    # update progress
    pbar.update(10)
    # mask population raster file with the shape of boundary of area of interest
    _population_raster_path = get_data_path("Bevoelkerung_100m-Gitter_raster.tif", "data")
    with rasterio.open(_population_raster_path) as src:
        out_image, out_transform = rasterio.mask.mask(src, [boundary], crop=True)
        out_meta = src.meta
    out_meta.update(
        {
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )
    # update progress
    pbar.update(40)
    # save the cliped population raster
    if not api_use:
        _selected_population_raster = output_folder + "\\" + "population_raster.tif"
        with rasterio.open(_selected_population_raster, "w", **out_meta) as dest:
            dest.write(out_image)
    # update progress
    pbar.update(10)

    #### get population in the grid_data
    # read the population hdf file
    _population_path = get_data_path("population.hdf5", "data")
    df = pd.read_hdf(_population_path)
    # update progress
    pbar.update(20)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["x_mp_100m"], df["y_mp_100m"]), crs="EPSG:3035"
    )
    gdf_proj = gdf.to_crs(4326)
    grid_data.census_data.population = intersection_with_area(gdf_proj, grid_data.area)
    # update progress
    pbar.update(20)
    # close progress bar
    pbar.close()
