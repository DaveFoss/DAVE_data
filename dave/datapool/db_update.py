# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import timeit

from tqdm import tqdm

from dave.datapool.oep_request import oep_request
from dave.io.database_io import db_availability, drop_collection, from_mongo, to_mongo
from dave.settings import dave_settings


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
    pass
    # # set progress bar
    # pbar = tqdm(
    #     total=100,
    #     desc="update data from OSM: ",
    #     position=0,
    #     bar_format=dave_settings()["bar_format"],
    # )


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
