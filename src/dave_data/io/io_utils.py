# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from copy import deepcopy

from geopandas import GeoSeries
from pandapower.io_utils import FromSerializableRegistry, to_serializable, with_signature

from dave.dave_structure import create_empty_dataset, davestructure


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
            from dave_client.io.file_io import from_json_string

            return from_json_string(self.obj)
        else:
            dave_dataset = create_empty_dataset()
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


@to_serializable.register(GeoSeries)
def json_series(obj):
    data = with_signature(obj, obj.to_json())
    data.update({"dtype": str(obj.dtypes), "typ": "geoseries", "crs": obj.crs})
    return data
