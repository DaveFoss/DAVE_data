import requests
from owslib.wms import WebMapService
from osgeo import gdal, ogr


def request_building_height(grid_data):
    boundary = grid_data.area.geometry.unary_union
    boundary_bbox = boundary.bounds
    print('we are here')
    # wms of building block height
    wms = WebMapService('https://copernicus.discomap.eea.europa.eu/arcgis/services/UrbanAtlas/UA_BuildingHeights_2012_10m/ImageServer/WMSServer?request=GetCapabilities&service=WMS', version='1.1.1')
    
    
    
    
    img = wms.getmap(layers=['0'],
                    styles=['default'],
                    srs='EPSG:4326',
                    bbox=boundary_bbox,
                    size=(300, 250),
                    format='image/jpeg',
                    transparent=True
                    )
    out = open('jpl_mosaic_visb.jpg', 'wb')
    out.write(img.read())
    out.close()
    
    raster_to_point(out)
    
    

def raster_to_point(raster):
    print('return point shapefile')
