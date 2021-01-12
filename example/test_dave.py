import os
from dave.create import create_grid


"""
This is a example file for testing dave
"""

########## Examples for grid area definition #########################
# test target by plz
_postalcode_1 = ['34225']  # Baunatal
_postalcode_2 = ['37085', '37075', '37083', '37079', '37081', '37073', '37077']  # Göttingen
_postalcode_3 = ['ALL']

# test target by town_name
_town_name_1 = ['Göttingen']
_town_name_2 = ['KAsSel', 'Baunatal']
_town_name_3 = ['ALL']

# test target by federal state
_federal_state_1 = ['Hessen']
_federal_state_2 = ['HeSsEn', 'SchleSWIg-HOLstein']
_federal_state_3 = ['ALL']

# test target by nuts-region
_nuts_1 = ['DE']  # nuts level 0
_nuts_2 = ['DE11A', 'DE11B']  # nuts level 3
_nuts_3 = ['DEF', 'DE60']  # example for diffrent nuts level combined(1 and 2)


# test own shape
# Hertingshausen is a part from the Town Baunatal. (ca. 500 relevant Buildings)
_own_area = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'


##################### test main function ##########################
"""
This is the main function for DaVe with all possible parameters.
For testing you can use the pre defined variables on the top or own ones.
"""

grid_data = create_grid(postalcode=None,
                        town_name=None,
                        federal_state=None,
                        nuts_region=None,
                        own_area=_own_area,
                        power_levels=['LV'],
                        gas_levels=[],
                        plot=True,
                        convert=False,  # if True a second return variable must be defined
                        opt_model=False,
                        transformers=False,
                        renewable_powerplants=False,
                        conventional_powerplants=False,
                        loads=False)
