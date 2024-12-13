"""
Description: This module retrieve data from HotMaps for any bounding box of interest,
and returns the clipped raster file in its original EPSG and the vector file in the
EPSG of interest (defined in the request).
The current available layer names are as below:
1. Heat density total
2. Final energy demand density for space heating and domestic hot water - Residential
3. Final energy demand density for space heating and domestic hot water - Non-Residential
4. Space cooling needs density
5. Building gross floor area density - Residential
6. Building gross floor area density - Non-Residential
7. Building gross floor area density - Total
8. Building construction period - until 1975
9. Building construction period - 1975 - 1990
10. Building construction period - 1990 - 2000
11. Building construction period - 2000 - 2014
12. Population total
13. Potential solar thermal collectors - rooftop
14. Potential solar thermal collectors - open field
License: MIT License.
"""

from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import (
    hotmaps_request,
)

# from dave_data.datapool.hotmaps.hotmaps_request import hotmaps_request

hotmaps_result = hotmaps_request(
    "Potential solar thermal collectors - open field",
    (14.348144531250002, 51.7406361640977, 14.3701171875, 51.754240074033525),
    4326,
)

# bbox_in_Eu = (14.348144531250002, 51.7406361640977, 14.3701171875, 51.754240074033525)
# bbox_outside_EU = (35.71436246138891, 51.38223366566746, 35.719158696607096, 51.39866831101444)
