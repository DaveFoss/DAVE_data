# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import os
from copy import deepcopy

import geopandas as gpd
import pandas as pd
from pandapower.io_utils import FromSerializableRegistry, to_serializable, with_signature

import dave
from dave.dave_structure import davestructure
from dave.toolbox import get_data_path


def archiv_inventory(grid_data, read_only=False):
    """
    This function check if a the dave archiv already contain the dataset.
    Otherwise the dataset name and possibly the inventory list were created
    """
    # check if inventory file exists
    inventory_path = get_data_path("inventory.csv", "dave_archiv")
    # dataset parameters
    target_input = grid_data.target_input.iloc[0]
    postalcode = target_input.data if target_input.typ == "postalcode" else "None"
    town_name = target_input.data if target_input.typ == "town name" else "None"
    federal_state = target_input.data if target_input.typ == "federal state" else "None"
    if os.path.isfile(inventory_path):
        # read inventory file
        inventory_list = pd.read_csv(inventory_path)
        # create dataset file
        dataset_file = pd.DataFrame(
            {
                "postalcode": str(postalcode),
                "town_name": str(town_name),
                "federal_state": str(federal_state),
                "power_levels": str(target_input.power_levels),
                "gas_levels": str(target_input.gas_levels),
                "dave_version": grid_data.dave_version,
            },
            index=[0],
        )
        # check if archiv already contain dataset
        inventory_check = inventory_list.drop(columns=["id"])
        inventory_check_res = inventory_check == dataset_file.iloc[0]
        inventory_index = inventory_check_res[inventory_check_res.all(axis="columns")].index
        if not inventory_index.empty:
            # in this case the dataset already exists in the archiv
            file_id = inventory_list.loc[inventory_index[0]].id
            file_name = f"dataset_{file_id}"
            return True, file_name
        else:
            # --- in this case the dataset don't exist already in the archiv
            # set file id and name
            file_id = inventory_list.tail(1).iloc[0].id + 1
            file_name = f"dataset_{file_id}"
            if not read_only:
                # create inventory entry
                dataset_entry = pd.DataFrame(
                    {
                        "id": file_id,
                        "postalcode": [postalcode],
                        "town_name": [town_name],
                        "federal_state": [federal_state],
                        "power_levels": [target_input.power_levels],
                        "gas_levels": [target_input.gas_levels],
                        "dave_version": grid_data.dave_version,
                    }
                )
                inventory_list = inventory_list.append(dataset_entry)
                inventory_list.to_csv(inventory_path, index=False)
            return False, file_name
    else:
        # --- archiv don't contain the dataset because it's empty
        # set file id and name
        file_id = 1
        file_name = f"dataset_{file_id}"
        if not read_only:
            # create inventory file
            inventory_list = pd.DataFrame(
                {
                    "id": file_id,
                    "postalcode": [postalcode],
                    "town_name": [town_name],
                    "federal_state": [federal_state],
                    "power_levels": [target_input.power_levels],
                    "gas_levels": [target_input.gas_levels],
                    "dave_version": grid_data.dave_version,
                }
            )
            inventory_list.to_csv(inventory_path, index=False)
        return False, file_name


def isinstance_partial(obj, cls):
    if isinstance(obj, davestructure):
        return False
    return isinstance(obj, cls)


class FromSerializableRegistryDaVe(FromSerializableRegistry):
    from_serializable = deepcopy(FromSerializableRegistry.from_serializable)
    class_name = ""
    module_name = ""

    @from_serializable.register(class_name="davestructure", module_name="dave.dave_structure")
    def davestructure(self):
        if isinstance(self.obj, str):  # backwards compatibility
            from dave.io import from_json_string

            return from_json_string(self.obj)
        else:
            dave_dataset = dave.create_empty_dataset()
            dataset = None
            for key in dave_dataset.keys():
                if (not isinstance(dave_dataset[key], str)) and (
                    next(iter(self.obj)) in dave_dataset[key].keys()
                ):
                    dataset = dave_dataset[key]
                elif isinstance(dave_dataset[key], davestructure):
                    for key_sec in dave_dataset[key].keys():
                        if next(iter(self.obj)) in dave_dataset[key][key_sec].keys():
                            dataset = dave_dataset[key][key_sec]
            if dataset is None:
                dataset = dave_dataset
            dataset.update(self.obj)
            return dataset


@to_serializable.register(davestructure)
def json_dave(obj):
    net_dict = {k: item for k, item in obj.items() if not k.startswith("_")}
    data = with_signature(obj, net_dict)
    return data


@to_serializable.register(gpd.GeoSeries)
def json_series(obj):
    data = with_signature(obj, obj.to_json())
    data.update({"dtype": str(obj.dtypes), "typ": "geoseries", "crs": obj.crs})
    return data
