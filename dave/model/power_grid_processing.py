import pandapower as pp

from dave import dave_output_dir


# hier wird das Stromnetz modell aufbereitet damit ein LAstfluss konvergiert udn sonstige fehler weg machen

def power_processing(net_power):
    
    print('run power grid processing')
    print('-------------------------')
    # run network diagnostic
    diagnostic = pp.diagnostic(net_power)
    # --- clean up failures detected by the diagnostic tool
    # delete disconected buses and the elements connected to them
    if 'disconnected_elements' in diagnostic.keys():
        for idx in  range(0,len(diagnostic['disconnected_elements'])):
            drop_buses = diagnostic['disconnected_elements'][idx]['buses']
            pp.drop_buses(net_power, drop_buses) 
    # change lines with impedance close to zero to switches
    if 'impedance_values_close_to_zero' in diagnostic.keys():
        lines = diagnostic['impedance_values_close_to_zero'][0]['line']
        for line_index in lines:
            pp.create_replacement_switch_for_branch(net_power, element='line', idx = line_index)
        pp.drop_lines(net_power, lines=lines)
        
    # clean up overloads
    if 'overload' in diagnostic.keys():
        pass
        # wie bekomme ich raus welche Elemente überlastet sind, damit ich da am besten gegenwirken kann
        # Bei dem Transnet modell z.B. die sgens auf 0.1 runter scalieren, wie lese ich das aus?
    
    # save grid model in the dave output folder                   das noch in create verschieben??
    file_path = dave_output_dir + '\\dave_power_grid.p'
    pp.to_pickle(net_power, file_path)
    
    return net_power