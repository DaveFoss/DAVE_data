# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import timeit

from pyrosm import OSM, get_data
from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.io.database_io import db_availability, drop_collection, from_mongo, to_mongo
from dave.settings import dave_settings


def change_oep_version(table, new_version):
    """
    This function changes the version for an oep table to the latest
    """
    filepath = dave_settings()["dave_dir"] + "\\settings.py"
    # read settings file
    with open(filepath) as f:
        lines = f.readlines()
    # adjust oep version if there is a newer one
    table = "ego_pf_hv_line"
    for line in lines:
        if table in line:
            # get line index
            line_idx = lines.index(line)
            # change version
            line_split = line.split('"')
            for segment in line_split:
                if segment.startswith("version"):
                    line = line.replace(segment, new_version)
                    break
            lines[line_idx] = line
            break
    # write changed lines into settings file
    with open(filepath, "w") as f:
        f.writelines(lines)
        f.close()


def oep_update():
    """
    This function updates the relevant data from the open energy platform
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="update data from OEP: ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    relevant_tables = dave_settings()["oep_tables"]
    # check for new versions and update database
    for table in relevant_tables.keys():
        # get dataset from oep
        dataset, meta_data = oep_request(
            table=table,
            db_update=True,
        )
        if "version" in dataset.keys():
            # check for latest version
            latest_version = dataset.version.unique()[-1]
            # filter dataset to latest version
            dataset = dataset[dataset.version == latest_version]
            # check if database need an update
            if db_availability(collection_name=table):
                # In the database is allready an collection for this dataset => drop old one
                db_dataset = from_mongo(database="power", collection=table)
                current_version = db_dataset.version.unique()[0]
                if current_version != latest_version:
                    # drop existing collection
                    drop_collection(database="power", collection=table)
                    # Write dataset to database
                    to_mongo(database="power", collection=table, data_df=dataset)
                    # change version in dave settings
                    change_oep_version(table=table, new_version=latest_version)
            else:
                # Write dataset to database
                to_mongo(database="power", collection=table, data_df=dataset)
        elif not db_availability(
            collection_name=table
        ):  # !!! How to check dataset without version if there is an update? (e.g. powerplants)
            # Write dataset to database
            to_mongo(database="power", collection=table, data_df=dataset)
        # update progress
        pbar.update(100 / len(relevant_tables.keys()))


def osm_update():
    """
    This function updates the relevant data from the OpenStreetMap
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="update data from OSM: ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # considerd area
    osm_area = dave_settings()["osm_area"]
    # download data from osm
    filepath = get_data(
        osm_area, directory=dave_settings()["dave_dir"] + "\\datapool\\data", update=True
    )
    # Initialize the OSM object
    osm = OSM(filepath)
    pbar.update(10)
    # filter data from local osm file and write to database
    for data_type in dave_settings()["osm_tags"].keys():
        # create collection name
        collection = f"osm_{data_type}_{osm_area}"
        # get data parameter
        data_param = dave_settings()["osm_tags"][data_type]
        # filter data_type
        dataset = osm.get_data_by_custom_criteria(
            custom_filter={data_param[0]: data_param[1]},
            # Keep data matching the criteria above
            filter_type="keep",
            keep_nodes=True if "node" in data_param[2] else False,
            keep_ways=True if "way" in data_param[2] else False,
            keep_relations=True if "relation" in data_param[2] else False,
        )
        if db_availability(collection_name=collection):
            # drop existing collection
            drop_collection(database="geo", collection=collection)
        # Write dataset to database
        to_mongo(database="geo", collection=collection, data_df=dataset)
        # update progress
        pbar.update(90 / len(dave_settings()["osm_tags"].keys()))


if __name__ == "__main__":
    # start runtime
    _start_time = timeit.default_timer()
    # check if database is available
    if db_availability():
        print("-------------------------Update DAVE Database-------------------------")
        # update oep data
        oep_update()
        # update osm data
        osm_update()
        # update local data
    else:
        print("Database is not available")
    # stop and show runtime
    _stop_time = timeit.default_timer()
    print("runtime = " + str(round((_stop_time - _start_time) / 60, 2)) + " min")
