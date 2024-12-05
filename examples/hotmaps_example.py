"""
Description: This module retrieve the total heat demand of buildings from HotMaps and plot them with the osm background.
License: MIT License.
"""
from DAVE_data.src.dave_data.datapool.hotmaps.hotmaps_request import hotmaps_request

hotmaps_result = hotmaps_request(
    "Heat density total",
    (14.348144531250002, 51.7406361640977, 14.3701171875, 51.754240074033525),
    4326
)

#(14.348144531250002, 51.7406361640977, 14.3701171875, 51.754240074033525)
#berlin_bbox = (13.077393,52.350617,13.626709,52.638065)
