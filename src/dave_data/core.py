import datetime

import pandas as pd


class MetaData:
    """
    Meta Data Class for DAVE_data.

    Parameters
    ----------
    source_license : str
    source_date : datetime.date or None


    Attributes
    ----------
    license : str
    organisation : str
    source_date : datetime.date or None
    fetch_date : datetime.date
    source meta : dict
    """

    def __init__(
        self,
        source_license,
        source_date=None,
        organisation=None,
        source_url=None,
        source_meta=None,
    ):
        self.license = source_license
        self.source_date = source_date
        self.fetch_date = datetime.datetime.now(tz=datetime.timezone.utc)
        self.source_url = source_url
        self.organisation = organisation
        if source_meta is None:
            source_meta = {}
        self.source_meta = source_meta


class Data:
    """
    Attributes
    ----------
    name
    """

    def __init__(
        self,
        name,
        description=None,
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
