from setuptools import setup, find_packages

# read information files
with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')
with open('CHANGELOG.rst', 'rb') as f:
    changelog = f.read().decode('utf-8')

# create long description
long_description = '\n\n'.join((readme, changelog))

# define setup
setup(
    name='dave',
    version='1.0.5',
    author='Tobias Banze',
    author_email='tobias.banze@iee.fraunhofer.de',
    description='DaVe is a tool for automatic energy grid generation',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    install_requires=['Shapely',
                      'GDAL',
                      'Fiona',
                      'pyproj',
                      'Rtree',
                      'geopandas',
                      'matplotlib',
                      'geopy',
                      'descartes',
                      'pandapower',
                      'rasterio',
                      'contextily',
                      'tqdm',
                      'fastapi',
                      'uvicorn',
                      'pytest',
                      'pytest-xdist',
                      'pandapipes',
                      'tables'],
    packages=find_packages(),
    include_package_data=True
)
