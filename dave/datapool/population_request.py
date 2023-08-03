
import rasterio
import rasterio.mask
from dave.settings import dave_settings
from dave.toolbox import get_data_path

output_folder=dave_settings()["dave_output_dir"]

def request_population(grid_data):
    
    # get the boundary of area of interest
    boundary = grid_data.area.geometry.unary_union
    
    # mask population raster file with the shape of boundary of area of interest
    _population_raster_path = get_data_path("Bevoelkerung_100m-Gitter_raster.tif", "data")
    with rasterio.open(_population_raster_path) as src:
        out_image, out_transform = rasterio.mask.mask(src, [boundary], crop=True)
        out_meta = src.meta
    
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

    # save the cliped population raster 
    _selected_population_raster = output_folder + "\\" + "population_raster.tif"
    with rasterio.open(_selected_population_raster, "w", **out_meta) as dest:
        dest.write(out_image)
        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          