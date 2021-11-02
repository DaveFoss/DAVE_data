import pandapipes as ppi


def gas_processing(net_gas):
    """
    This function run a diagnosis of the pandapipes network and clean up occurring failures.
    Furthermore the grid will be adapt so all boundarys be respected.

    INPUT:
        **net** (attrdict) - pandapipes attrdict

    OUTPUT:
        **net** (attrdict) - A cleaned up and if necessary optimized pandapipes attrdict
    """
    return net_gas
    # hier wird das Gasnetzmodell nach dem es in pandapipes erstellt wurde, aufbereitet damit ein
    # lastfluss konvergiert und sonstige Fehler bereinigen
