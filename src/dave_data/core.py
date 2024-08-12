import pandas as pd


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
