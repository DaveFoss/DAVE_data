Change Log
=============


[1.2.0] - (2023--) 
----------------------
- [MOVED]   model module to DAVE client
- [MOVED]   io module to DAVE client
- [CHANGED] archiv i/o function in seperated file 
- [MOVED]   plotting module to DAVE client
- [ADDED]   building height based on raster data
- [ADDED]   extend api with functions for database managment
- [ADDED]   environment files for the possibility to install DAVE via mamba
- [ADDED]   converter for the multiphysical network simulator MYNTS
- [ADDED]   population data from census and the possibility to request the raster data
- [ADDED]   importer for data from the gassimulation softwaretool SIMONE
- [ADDED]   api restriction by user role
- [ADDED]   option to choose year for nuts regions (2013, 2016, 2021)
- [ADDED]   geopackage as possible output format
- [ADDED]   extend geographical data with more landuse information and data for waterways
- [CHANGED] input parameters for geographical objects reduced to one parameter "geodata" 


[1.1.0] - 2022-11-03
----------------------
- [EVENT]   first open accessible "software as a service" platform version
- [ADDED]   algorithm for automated deployment
- [ADDED]   api authentication
- [ADDED]   own database for DAVE (mongo db) and restructured data requests
- [ADDED]   algorithm for regular automated database updates
- [ADDED]   algorithm for regular automated database dump
- [EVENT]   DAVE licensed under a three clause bsd license 
- [ADDED]   geography module and separated geographical data from grid model generation
- [ADDED]   restructured target area functions
- [FIXED]   osm gateway timeout
- [FIXED]   stack overflow error
- [ADDED]   different years as option for nuts regions 
- [CHANGED] renamed building category from "for_living" to "residential" 
- [ADDED]   function for intersection with considering mixed geometries 
- [FIXED]   duplicate naming
- [ADDED]   topology cleanup for power and gas models 
- [CHANGED] power components script splitted to separate scripts according to the components
- [CHANGED] bus naming in ehv and hv models from "bus0/bus1" to "from/to_bus" 
- [ADDED]   gaslib converter
- [CHANGED] channel for required packages to only "conda forge" because of anaconda terms changes
- [ADDED]   gas component: source, sink, compressor
- [ADDED]   pandapipes converter
- [ADDED]   function to transform address into coordinates


[1.0.6] - 2021-10-20
----------------------
- [ADDED]   option for output folder path
- [FIXED]   wrong/missing types at pandapower converter
- [FIXED]   missing crs definitions
- [ADDED]   application programming interface (api) module
- [CHANGED] build seperated io modul, changed structure and moved existing io functions to that
- [CHANGED] rebuild from/to hdf functions and merged with from/to archiv 
- [ADDED]   functions for serialization
- [ADDED]   automated build of docker images from ci (with kaniko)
- [ADDED]   basic test structure
- [ADDED]   setup file
- [ADDED]   uniform code style (with black) via pre-commit hooks
- [ADDED]   uniform import order (with isort) via pre-commit hooks
- [CHANGED] moved dave dir paths to settings file
- [ADDED]   interface to api, for reach own database (mongo db)

[1.0.5] - 2021-03-21
----------------------
- [ADDED]   substations for other voltage levels
- [CHANGED] move ehv substations to components power
- [FIXED]   missing line and trafo data within pandapower converting

[1.0.4] - 2021-03-18
----------------------
- [CHANGED] pandapower converter function restructured
- [CHANGED] condition deleted that more than one bus must exist for transformers

[1.0.3] - 2021-03-04
----------------------
- [ADDED]   description in install tutorial for using DaVe in PyCharm  
- [ADDED]   runtime count

[1.0.2] - 2021-02-10
----------------------
- [ADDED]   progress bars
- [FIXED]   overwriting points in voronoi calculation 

[1.0.1] - 2021-01-26
----------------------
- [FIXED]   replaced deprecated shapely "cascaded union" function with "unary_union" function
- [CHANGED] voronoi function expanded with dynamic corner points
- [ADDED]   json to pp converting function with considering geometries
- [ADDED]   pp to json converting function with considering geometries
- [ADDED]   nuts regions as input option for grid area
- [ADDED]   possibility to choose components individually
- [CHANGED] use scigridgas igginl dataset instead of lkd_eu dataset for high pressure gas level

[1.0.0] - 2020-12-21
----------------------
- [EVENT]   first usable DaVe version

[0.0.0] - 2020-02-05
----------------------
- [EVENT]   started DaVe development
