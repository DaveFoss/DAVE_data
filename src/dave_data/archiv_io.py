# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from os import listdir, path

from dave_data.io.file_io import from_hdf, to_hdf
from pandas import DataFrame, read_csv

from dave_data.toolbox import get_data_path


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
    if path.isfile(inventory_path):
        # read inventory file
        inventory_list = read_csv(inventory_path)
        # create dataset file
        dataset_file = DataFrame(
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
                dataset_entry = DataFrame(
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
            inventory_list = DataFrame(
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


def from_archiv(dataset_name):
    """
    This functions reads a dave dataset from the dave internal archiv
    """
    # check if file exist
    files_in_archiv = listdir(get_data_path(dirname="dave_archiv"))
    if dataset_name in files_in_archiv:
        grid_data = from_hdf(get_data_path(dataset_name, "dave_archiv"))
        return grid_data
    else:
        print("The requested file is not found in the dave archiv")


def to_archiv(grid_data):
    """
    This functions stores a dave dataset in the dave internal archiv
    """
    # check if file already exists and create file name for archiv
    file_exists, file_name = archiv_inventory(grid_data)
    # create archive file if the dataset does not exists in the archiv
    if not file_exists:
        to_hdf(grid_data, get_data_path(f"{file_name}.h5", "dave_archiv"))
    else:
        print(
            "The dataset you tried to save already exist in the DaVe archiv"
            f' with the name "{file_name}"'
        )
    return file_name
