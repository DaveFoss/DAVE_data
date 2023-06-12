# Copyright (c) 2022-2023 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import timeit

from pyrosm import OSM, get_data
from pyrosm.data import sources
from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.io.database_io import (
    create_database,
    db_availability,
    drop_collection,
    from_mongo,
    info_mongo,
    to_mongo,
)
from dave.settings import dave_settings
from dave.toolbox import get_data_path


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
    # close progress bar
    pbar.close()


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
    # in the case of considering germany the data has to be considered in supregions because otherwise there could be an memory error
    if osm_area == "germany":
        sub_regions = [
            "baden_wuerttemberg",
            "bayern",
            "brandenburg",
            "bremen",
            "hamburg",
            "hessen",
            "mecklenburg_vorpommern",
            "niedersachsen",
            "nordrhein_westfalen",
            "rheinland_pfalz",
            "saarland",
            "sachsen",
            "sachsen_anhalt",
            "schleswig_holstein",
            "thueringen",
        ]  # hint: The dataset "brandenburg" at geofabrik contains berlin

    for idx, region in enumerate(sub_regions):
        # download data from osm
        filepath = get_data(
            region, directory=dave_settings()["dave_dir"] + "\\datapool\\data\\osm", update=True
        )
        # Initialize the OSM object
        osm = OSM(filepath)
        pbar.update(10 / len(sub_regions))
        # filter data from local osm file and write to database
        for data_type in dave_settings()["osm_tags"].keys():
            print(f"{region}_{data_type}")  # !!! only for testing
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
            if idx == 0:
                if db_availability(collection_name=collection):
                    # drop existing collection
                    drop_collection(database="geo", collection=collection)
                # Write dataset to database
                to_mongo(database="geo", collection=collection, data_df=dataset)
            else:
                # Write dataset to database in existing collection
                to_mongo(database="geo", collection=collection, data_df=dataset, merge=True)
            # update progress
            pbar.update(90 / (len(sub_regions) * len(dave_settings()["osm_tags"].keys())))
    # close progress bar
    pbar.close()


def local_data_update():
    """
    This function writes the local data from the Datapool into the database
    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="update data from local datapool: ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )
    # define datasets
    datasets_geo = ["postalcodesger.h5", "federalstatesger.h5", "nuts_regions.h5"]
    datasets_gas = ["gas_storage_ugs.h5", "scigridgas_igginl.h5", "scigridgas_iggielgn.h5"]
    datasets_power = ["household_power_consumption.h5"]
    number_datasets = len(datasets_geo + datasets_gas + datasets_power)
    # write geo dataset to database
    for file in datasets_geo:
        to_mongo(
            database="geo",
            collection=None,
            data_df=None,
            filepath=get_data_path(file, "data"),
            merge=False,
        )
        # update progress
        pbar.update(100 / number_datasets)
    # write gas dataset to database
    for file in datasets_gas:
        to_mongo(
            database="gas",
            collection=None,
            data_df=None,
            filepath=get_data_path(file, "data"),
            merge=False,
        )
        # update progress
        pbar.update(100 / number_datasets)
    # write power dataset to database
    for file in datasets_power:
        to_mongo(
            database="power",
            collection=None,
            data_df=None,
            filepath=get_data_path(file, "data"),
            merge=False,
        )
        # update progress
        pbar.update(100 / number_datasets)
    # close progress bar
    pbar.close()


def update_database():
    # start runtime
    _start_time = timeit.default_timer()
    # set parameter for rebuild the db e.g. in the case the db is crashed
    rebuild_db = True if len(info_mongo().keys()) == 0 else False
    # check if database is available
    if db_availability():
        print("-------------------------Update DAVE Database-------------------------")
        if rebuild_db:
            # create databases
            create_database(database_names=["geo", "gas", "power"])
            # update local data
            local_data_update()
        # update oep data
        oep_update()

        # update osm data
        # osm_update()  # !!! memory error

    else:
        print("Database is not available")
    # stop and show runtime
    _stop_time = timeit.default_timer()
    print("runtime = " + str(round((_stop_time - _start_time) / 60, 2)) + " min")
