import os
import timeit

from dave.create import create_grid


"""
This is a example file for testing dave
"""

# start runtime
_start_time = timeit.default_timer()


########## Examples for grid area definition #########################
# test target by plz
_postalcode_1 = ['34225']
_postalcode_2 = ['37085', '37075', '37083', '37079', '37081', '37073', '37077']  # Göttingen
_postalcode_3 = ['ALL']

# test target by town_name
_town_name_1 = ['Baunatal']
_town_name_11 = ['Göttingen']
_town_name_2 = ['KAsSel', 'Baunatal']
_town_name_3 = ['ALL']

# test target by federal state
_federal_state_1 = ['Hessen']
_federal_state_2 = ['HeSsEn', 'SchleSWIg-HOLstein']
_federal_state_3 = ['ALL']
_federal_state_NB1 = ['Baden-Württemberg']  # Transnet BW Gebiet
_federal_state_NB2 = ['Thüringen', 'Sachsen', 'Sachsen-Anhalt', 'Brandenburg',
                      'Berlin', 'Mecklenburg-Vorpommern', 'Hamburg']  # 50 Hertz Gebiet

# test own shape (Hertingshausen is a part from the Town Baunatal).
# It has 500 relevant Buildings(for living and commercial))
_own_area = os.path.dirname(os.path.realpath(__file__))+'\\hertingshausen\\hertingshausen.shp'


##################### test with main function ##########################
"""
grid_data = create_grid(postalcode=None,
                       town_name=None,
                       federal_state=None,
                       own_area=_own_area_tn,
                       power_levels=['HV'],
                       gas_levels=[],
                       plot=False,
                       convert = False)
"""
"""
grid_data  = create_grid(postalcode=None,
                                    town_name=None,
                                    federal_state=['Hessen'],
                                    own_area=None,
                                    power_levels=['EHV', 'HV'],
                                    gas_levels=[],
                                    plot=False,
                                    convert = False)
"""
"""
grid_data, pp_model  = create_grid(postalcode=None,
                                   town_name=None,
                                   federal_state=None,
                                   own_area=_own_area,
                                   power_levels=['LV'],
                                   gas_levels=[],
                                   plot=False,
                                   convert = True,
                                   opt_model = False)
"""
#"""
grid_data = create_grid(postalcode=None,
                        town_name=_town_name_1,
                        federal_state=None,
                        own_area=None,
                        power_levels=['MV'],
                        gas_levels=[],
                        plot=False,
                        convert=False,
                        opt_model=False)
#"""


# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(round((_stop_time - _start_time)/60, 2)) + 'min')

"""
# check time for special command
# start runtime
_start_time = timeit.default_timer()

        grid_data.lv_data.lv_lines.at[line.name, 'to_bus'] = dave_name

# stop and show runtime
_stop_time = timeit.default_timer()
print('runtime = ' + str(_stop_time - _start_time) + 'sek')
"""
