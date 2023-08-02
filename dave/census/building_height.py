
import rasterio
import rasterio.mask
from rasterio.features import geometry_mask,geometry_window
import shapely
import geopandas as gpd
from fiona.crs import from_epsg
import os
import fiona
from dave.settings import dave_settings
from osgeo import ogr
from osgeo import gdal



output_folder=dave_settings()["dave_output_dir"]

def request_building_height(grid_data):
    
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
    _building_height_raster = os.path.dirname(os.path.realpath(__file__+ "../../")) + "\\datapool\\data\\building_height\\DE001_BERLIN_UA2012_DHM_V030.tif"
    #os.chdir("../node/sdatapool/data/Bevoelkerung_100m-Gitter_raster.tif")
    
    # reprojecting the raster
    output_projected_raster_file = os.path.dirname(os.path.realpath(__file__)) + "\\DE001_BERLIN_UA2012_DHM_V030_projected.tif"
    warp = gdal.Warp(output_projected_raster_file,_building_height_raster,dstSRS='EPSG:4326')
    warp = None

    # check if the two datasets have overlap
    
   
    
    # mask population raster file with the shape of boundary of area of interest
    with rasterio.open(output_projected_raster_file) as src:
        print('check thisssss')
        print(geometry_window(src, shapes, pad_x=0, pad_y=0))
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    
   
    
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

    # if out_image:
        
    # save the cliped population raster 
    _selected__building_height_raster = output_folder + "\\" + "building_height_raster.tiff"
    with rasterio.open(_selected__building_height_raster, "w", **out_meta) as dest:
        dest.write(out_image)
        
    # delete the boundary shape
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(_boundary):
          driver.DeleteDataSource(_boundary)

    os.remove(output_projected_raster_file)

