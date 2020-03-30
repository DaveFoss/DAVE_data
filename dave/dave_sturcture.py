import copy
import pandas as pd
from pandapower.auxiliary import ADict


class davestructure(ADict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(args[0], self.__class__):
            net = args[0]
            self.clear()
            self.update(**net.deepcopy())

    def deepcopy(self):
        return copy.deepcopy(self)

    def __repr__(self):  # pragma: no cover
        r = 'This dave dataset includes the following parameter tables:'
        for tb in list(self.keys()):
            if not tb.startswith("_") and isinstance(self[tb], pd.DataFrame) and len(self[tb]) > 0:
                length = len(self[tb])
                r += f'\n   - {tb} ({length} {"elements" if length > 1 else "element"})'
            if not tb.startswith('_') and isinstance(self[tb], davestructure):
                r += f'\n   - {tb}:'
                for utb in list(self[tb].keys()):
                    if not utb.startswith("_") and isinstance(self[tb][utb], pd.DataFrame) and len(self[tb][utb]) > 0:
                        length = len(self[tb][utb])
                        r += f'\n\t   - {utb} ({length} {"elements" if length > 1 else "element"})'
        return r


