# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from dave.datapool import oep_request
from dave.io import db_availability, drop_collection, from_mongo, to_mongo
from dave.settings import dave_settings


def oep_update():
    # This function updates the relevant data from the open energy platform
    relevant_tables = dave_settings()["oep_tables"]
    # check for new versions and update database
    for table in relevant_tables.keys():
        # get dataset from oep
        dataset, meta_data = oep_request(
            schema=relevant_tables[table][0],
            table=table,
            geometry=relevant_tables[table][1],
            db_update=True,
        )
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


def osm_update():
    # This function updates the relevant data from the OpenStreetMap
    pass


if __name__ == "__main__":
    # check if database is available
    if db_availability():
        # update oep data
        oep_update()
        # update osm data
        osm_update()
        # update local data
    else:
        print("Database is not available")
