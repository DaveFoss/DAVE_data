import os
import pandas as pd
import geopandas as gpd
from pandapower.io_utils import with_signature, to_serializable

from dave.datapool import get_data_path
from dave.dave_structure import davestructure


def archiv_inventory(grid_data, read_only=False):
    """
    This function check if a the dave archiv already contain the dataset.
    Otherwise the dataset name and possibly the inventory list were created
    """
    # check if inventory file exists
    inventory_path = get_data_path('inventory.csv', 'dave_archiv')
    # dataset parameters
    target_input = grid_data.target_input.iloc[0]
    postalcode = target_input.data if target_input.typ == 'postalcode' else 'None'
    town_name = target_input.data if target_input.typ == 'town name' else 'None'
    federal_state = target_input.data if target_input.typ == 'federal state' else 'None'
    if os.path.isfile(inventory_path):
        # read inventory file
        inventory_list = pd.read_csv(inventory_path)
        # create dataset file
        dataset_file = pd.DataFrame({'postalcode': str(postalcode),
                                     'town_name': str(town_name),
                                     'federal_state': str(federal_state),
                                     'power_levels': str(target_input.power_levels),
                                     'gas_levels': str(target_input.gas_levels),
                                     'dave_version': grid_data.dave_version},
                                    index=[0])
        # check if archiv already contain dataset
        inventory_check = inventory_list.drop(columns=['id'])
        inventory_check_res = inventory_check == dataset_file.iloc[0]
        inventory_index = inventory_check_res[inventory_check_res.all(axis='columns')].index
        if not inventory_index.empty:
            # in this case the dataset already exists in the archiv
            file_id = inventory_list.loc[inventory_index[0]].id
            file_name = f'dataset_{file_id}'
            return True, file_name
        else:
            # --- in this case the dataset don't exist already in the archiv
            # set file id and name
            file_id = inventory_list.tail(1).iloc[0].id+1
            file_name = f'dataset_{file_id}'
            if not read_only:
                # create inventory entry
                dataset_entry = pd.DataFrame({'id': file_id,
                                              'postalcode': [postalcode],
                                              'town_name': [town_name],
                                              'federal_state': [federal_state],
                                              'power_levels': [target_input.power_levels],
                                              'gas_levels': [target_input.gas_levels],
                                              'dave_version': grid_data.dave_version})
                inventory_list = inventory_list.append(dataset_entry)
                inventory_list.to_csv(inventory_path, index=False)
            return False, file_name
    else:
        # --- archiv don't contain the dataset because it's empty
        # set file id and name
        file_id = 1
        file_name = f'dataset_{file_id}'
        if not read_only:
            # create inventory file
            inventory_list = pd.DataFrame({'id': file_id,
                                           'postalcode': [postalcode],
                                           'town_name': [town_name],
                                           'federal_state': [federal_state],
                                           'power_levels': [target_input.power_levels],
                                           'gas_levels': [target_input.gas_levels],
                                           'dave_version': grid_data.dave_version})
            inventory_list.to_csv(inventory_path, index=False)
        return False, file_name


@to_serializable.register(davestructure)
def json_dave(obj):
    net_dict = {k: item for k, item in obj.items() if not k.startswith("_")}
    d = with_signature(obj, net_dict)
    return d


@to_serializable.register(gpd.GeoSeries)
def json_series(obj):
    d = with_signature(obj, obj.to_json())
    d.update({'dtype': str(obj.dtypes), 'typ': 'geoseries', 'crs': obj.crs})
    return d
