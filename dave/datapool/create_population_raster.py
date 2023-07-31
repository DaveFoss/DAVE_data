
from osgeo import gdal
import csv
import os


# convert the csv grid file to xyz file
def csv_to_xyz(input_file, output_file):
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter= ';')
        next(reader)  # Skip the header row if present
        with open(output_file, 'w') as xyz_file:
            for row in reader:
                if len(row) >= 3:  # Ensure that there are at least 3 columns (X, Y, Z)
                     x, y, z = row[1:4]
                     xyz_file.write(f"{x} {y} {z}\n")

if __name__ == "__main__":
    input_csv_file = os.path.dirname(os.path.realpath(__file__)) + "\\data\\Zensus_Bevoelkerung_100m-Gitter.csv"
    output_xyz_file = os.path.dirname(os.path.realpath(__file__)) + "\\data\\population_raster.xyz"

    csv_to_xyz(input_csv_file, output_xyz_file)

# convert the xyz file to raster
output_raster_file = os.path.dirname(os.path.realpath(__file__)) + "\\data\\population_raster.tif"
raster = gdal.Translate(output_raster_file, output_xyz_file, outputSRS="EPSG: 3035")
raster = None
# reprojecting the raster
output_projected_raster_file = os.path.dirname(os.path.realpath(__file__)) + "\\data\\Bevoelkerung_100m-Gitter_raster.tif"
warp = gdal.Warp(output_projected_raster_file,output_raster_file,dstSRS='EPSG:4326')
warp = None

# remove temp files
os.remove(output_xyz_file)
os.remove(output_raster_file)