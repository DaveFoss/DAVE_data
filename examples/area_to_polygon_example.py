import os
from pathlib import Path

from dave_data.area_to_polygon import federal_state_to_polygon
from dave_data.area_to_polygon import file_to_polygon
from dave_data.area_to_polygon import nuts_to_polygon
from dave_data.area_to_polygon import postalcode_to_polygon
from dave_data.area_to_polygon import town_to_polygon

# --- postalcode to polygon options
# single postalcode
postalcode_single = ["34225"]
# multiple postalcode
postalcode_multi = [
    "37085",
    "37075",
    "37083",
    "37079",
    "37081",
    "37073",
    "37077",
]
# all postalcode in germany
postalcode_all = ["ALL"]  # all postal code areas in germany
# Now any of this variables can added to the postalcode_to_polygon function to get a suitable polygon
polygon_postal = postalcode_to_polygon(postalcode_single)

# --- town to polygon options
# singel town
town_single = ["Göttingen"]
# multiple towns
town_multi = ["KAsSel", "Baunatal"]
# all town names in germany
town_all = ["ALL"]
# Now any of this variables can added to the town_to_polygon function to get a suitable polygon
polygon_town = town_to_polygon(town_single)

# --- federal state to polygon options
# single federal state
federal_state_single = ["Hessen"]
# multiple federal state
federal_state_multi = ["HeSsEn", "SchleSWIg-HOLstein"]
# all federal states in germany
federal_state_all = ["ALL"]
# Now any of this variables can added to the federal_state_to_polygon function to get a suitable polygon
polygon_fed = federal_state_to_polygon(federal_state_all)

# --- nuts to polygon options
# single nuts
nuts_singel = ["DE"]  # nuts level 0
# multiple nuts at same level
nuts_multi_same = ["DE11A", "DE11B"]  # nuts level 3
# multiple nuts at diffrent levels
nuts_multi_diff = ["DEF", "DE60"]  #  diffrent nuts level combined(1 and 2)
# Now any of this variables can added to the nuts_to_polygon function to get a suitable polygon
polygon_nuts = nuts_to_polygon(nuts_multi_diff)

# --- file to polygon options
filepath = os.path.join(Path(__file__).parent, "hertingshausen.geojson")
polygon_file = file_to_polygon(filepath)
