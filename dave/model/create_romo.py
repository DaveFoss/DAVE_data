import pandas as pd
from tqdm import tqdm

from dave.settings import dave_settings
from dave.toolbox import multiline_coords


def create_romo(grid_data, api_use, output_folder):
    """
    This function creates a romo network based an the DaVe dataset

    INPUT:
        **grid_data** (attrdict) - calculated grid data from dave

    OUTPUT:

    """
    # set progress bar
    pbar = tqdm(
        total=100,
        desc="create romo model:                 ",
        position=0,
        bar_format=dave_settings()["bar_format"],
    )

    # return net


# def gas_processing(net_gas):
#     """
#     This function run a diagnosis of the pandapipes network and clean up occurring failures.
#     Furthermore the grid will be adapt so all boundarys be respected.

#     INPUT:
#         **net** (attrdict) - pandapipes attrdict

#     OUTPUT:
#         **net** (attrdict) - A cleaned up and if necessary optimized pandapipes attrdict
#     """
#     return net_gas
#     # hier wird das Gasnetzmodell nach dem es in pandapipes erstellt wurde, aufbereitet damit ein
#     # lastfluss konvergiert und sonstige Fehler bereinigen
