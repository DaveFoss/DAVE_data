Change Log
=============
upcoming release
----------------------
- [ADDED] substations for other voltage levels
- [CHANGED] move ehv substations to components power

[1.0.4] - 2021-03-18
----------------------
- [CHANGED] pandapower converter function restructured
- [CHANGED] condition deleted that more than one bus must exist for transformers

[1.0.3] - 2021-03-04
----------------------
- [ADDED] description in install tutorial for using DaVe in PyCharm  
- [ADDED] runtime count

[1.0.2] - 2021-02-10
----------------------
- [ADDED] progress bars
- [FIXED] overwriting points in voronoi calculation 

[1.0.1] - 2021-01-26
----------------------
- [FIXED] replaced deprecated shapely "cascaded union" function with "unary_union" function
- [CHANGED] voronoi function expanded with dynamic corner points
- [ADDED] json to pp converting function with considering geometries
- [ADDED] pp to json converting function with considering geometries
- [ADDED] nuts regions as input option for grid area
- [ADDED] possibility to choose components individually
- [CHANGED] use scigridgas igginl dataset instead of lkd_eu dataset for high pressure gas level
