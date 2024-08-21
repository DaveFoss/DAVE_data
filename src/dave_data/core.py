import datetime

import pandas as pd


class MetaData:
    """
    Meta Data Class for DAVE_data.

    Parameters
    ----------
    source_license
    source_date


    Attributes
    ----------
    license : str
    organisation : str
    source_date : str
    fetch_date : datetime.date
    source meta : dict
    """

    def __init__(self, source_license, source_date, organisation=None):
        self.license = source_license
        self.source_date = self._convert_date(source_date)
        self.fetch_date = datetime.datetime.now()
        self.source_url = None
        self.organisation = organisation
        self.source_meta = None

    def _convert_date(self, value):
        return ""


class Data:
    """
    Attributes
    ----------
    name
    """

    def __init__(
        self,
        name,
        description = None,
        data=None,
        meta=None,
        polygon=None,
        tags=None,
    ):
        """

        Parameters
        ----------
        data : geopandas.geoDataFrame
            Data table with the original data.
        organ
        """
        self.name = name
        self.description = description
        self.data = data  # geopandas.geoDataFrame
        self.meta = meta  # MetaData object
        self.polygon = polygon  # Searching polygon
        self.tags = tags  # list

    def store(self):
        pass

    def restore(self):
        pass


def compute(args):
    return max(args, key=len)


def get_data(datatype):
    """

    Parameters
    ----------
    datatype :str
        The category of your data.

    Returns
    -------
    pandas.Series

    Examples
    --------
    >>> get_data("building")
    Here is your building data.
    0    1
    1    2
    2    3
    3    4
    dtype: int64
    """
    print(f"Here is your {datatype} data.")
    return pd.Series([1, 2, 3, 4])
