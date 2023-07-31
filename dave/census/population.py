
import rasterio
import rasterio.mask
import shapely
import geopandas as gpd
from fiona.crs import from_epsg
import os
import fiona
from dave.settings import dave_settings
from osgeo import ogr


output_folder=dave_settings()["dave_output_dir"]

def request_population(grid_data):
    
    # get the boundary of area of interest
    boundary = grid_data.area.geometry.unary_union
    boundary_shape = shapely.wkt.loads(str(boundary))
    
    # convert the boundary to shape
    newdata = gpd.GeoDataFrame()
    newdata['geometry'] = None
    newdata.loc[0, 'geometry'] = boundary_shape
    newdata.crs = from_epsg(4326)
    _boundary = os.path.dirname(os.path.realpath(__file__)) + "\\boundary.shp"
    newdata.to_file(_boundary)
    
    with fiona.open(_boundary, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]
    
    # read population raster file
    _population_raster = os.path.dirname(os.path.realpath(__file__+ "../../")) + "\\datapool\\data\\Bevoelkerung_100m-Gitter_raster.tif"
    #os.chdir("../node/sdatapool/data/Bevoelkerung_100m-Gitter_raster.tif")
    # mask population raster file with the shape of boundary of area of interest
    with rasterio.open(_population_raster) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

    # save the cliped population raster 
    _selected_population_raster = output_folder + "\\" + "population_raster.tiff"
    with rasterio.open(_selected_population_raster, "w", **out_meta) as dest:
        dest.write(out_image)
        
    # delete the boundary shape
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(_boundary):
         driver.DeleteDataSource(_boundary)
             



    

