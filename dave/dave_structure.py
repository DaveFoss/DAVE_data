# Copyright (c) 2022 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

from copy import deepcopy

import pandas as pd
from pandapower.auxiliary import ADict


class davestructure(ADict):
    """
    This class is for showing a overview of the DaVe dataset in the python console
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(args[0], self.__class__):
            net = args[0]
            self.clear()
            self.update(**net.deepcopy())

    def __repr__(self):  # pragma: no cover
        titel = "This DaVe dataset includes the following parameter tables:"
        for key in list(self.keys()):
            if isinstance(self[key], pd.DataFrame) and not self[key].empty:
                length = len(self[key])
                titel += f'\n   - {key} ({length} {"elements" if length > 1 else "element"})'
            if isinstance(self[key], davestructure):
                titel += f"\n   - {key}:"
                for key2 in list(self[key].keys()):
                    if isinstance(self[key][key2], pd.DataFrame) and not self[key][key2].empty:
                        length = len(self[key][key2])
                        titel += (
                            f'\n\t   - {key2} ({length} {"elements" if length > 1 else "element"})'
                        )
                    if isinstance(self[key][key2], davestructure):
                        titel += f"\n\t   - {key2}:"
                        for key3 in list(self[key][key2].keys()):
                            if (
                                isinstance(self[key][key2][key3], pd.DataFrame)
                                and not self[key][key2][key3].empty
                            ):
                                length = len(self[key][key2][key3])
                                titel += f'\n\t\t   - {key3} ({length} {"elements" if length > 1 else "element"})'
        return titel
