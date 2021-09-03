import copy
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

    def deepcopy(self):
        return copy.deepcopy(self)

    def __repr__(self):  # pragma: no cover
        r = "This DaVe dataset includes the following parameter tables:"
        for tb in list(self.keys()):
            if isinstance(self[tb], pd.DataFrame) and not self[tb].empty:
                length = len(self[tb])
                r += f'\n   - {tb} ({length} {"elements" if length > 1 else "element"})'
            if isinstance(self[tb], davestructure):
                r += f"\n   - {tb}:"
                for utb in list(self[tb].keys()):
                    if isinstance(self[tb][utb], pd.DataFrame) and not self[tb][utb].empty:
                        length = len(self[tb][utb])
                        r += f'\n\t   - {utb} ({length} {"elements" if length > 1 else "element"})'
                    if isinstance(self[tb][utb], davestructure):
                        r += f"\n\t   - {utb}:"
                        for uutb in list(self[tb][utb].keys()):
                            if (
                                isinstance(self[tb][utb][uutb], pd.DataFrame)
                                and not self[tb][utb][uutb].empty
                            ):
                                length = len(self[tb][utb][uutb])
                                r += f'\n\t\t   - {uutb} ({length} {"elements" if length > 1 else "element"})'
        return r
