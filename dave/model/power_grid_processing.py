import pandapower as pp

from dave import dave_output_dir


def power_processing(net_power, min_vm_pu=0.95, max_vm_pu=1.05, max_line_loading=100, max_trafo_loading=100):
    """
    This function run a diagnosis a pandapower network and clean up occurring failures.
    Furthermore the grid will be adapt so all boundarys be respected.

    INPUT:
        **net_power** (attrdict) - PANDAPOWER attrdict with grid data

    OUTPUT:
        **net_power** (attrdict) - A cleaned up PANDAPOWER attrdict with grid data

    EXAMPLE:

    """
    print('run power grid diagnostic and processing')
    print('----------------------------------------')
    # run network diagnostic
    diagnostic = pp.diagnostic(net_power, report_style='None')
    # --- clean up failures detected by the diagnostic tool
    # delete disconected buses and the elements connected to them
    if 'disconnected_elements' in diagnostic.keys():
        for idx in range(0, len(diagnostic['disconnected_elements'])):
            drop_buses = diagnostic['disconnected_elements'][idx]['buses']
            pp.drop_buses(net_power, drop_buses)
    # change lines with impedance close to zero to switches
    if 'impedance_values_close_to_zero' in diagnostic.keys():
        lines = diagnostic['impedance_values_close_to_zero'][0]['line']
        for line_index in lines:
            pp.create_replacement_switch_for_branch(net_power, element='line', idx=line_index)
        pp.drop_lines(net_power, lines=lines)
    # correct invalid values
    if 'invalid_values' in diagnostic.keys():
        if 'gen' in diagnostic['invalid_values'].keys():
            for gen in diagnostic['invalid_values']['gen']:
                if (gen[1] == 'p_mw') and (gen[2] == 'nan'):
                    net_power.gen.at[gen[0], 'p_mw'] = 0
        if 'line' in diagnostic['invalid_values'].keys():
            drop_lines = []
            for line in diagnostic['invalid_values']['line']:
                if (line[1] == 'length_km') and (line[2] == 0):
                    pp.create_replacement_switch_for_branch(net_power, element='line', idx=line[0])
                    drop_lines.append(line[0])
            pp.drop_lines(net_power, lines=drop_lines)
                
        
        
        
        
    # run network diagnostic
    diagnostic = pp.diagnostic(net_power, report_style='None')
    # clean up overloads
    while 'overload' in diagnostic.keys():
        if (diagnostic['overload']['generation']) and (net_power.sgen.scaling.min() >= 0.1):
            # scale down sgens about 10%
            net_power.sgen.scaling -= 0.1
            # run diagnostic after scale down for a new report
            diagnostic = pp.diagnostic(net_power, report_style='None')
        elif (diagnostic['overload']['load']) and (net_power.load.scaling.min() >= 0.1):
            # scale down sgens about 10%
            net_power.load.scaling -= 0.1
            # run diagnostic after scale down for a new report
            diagnostic = pp.diagnostic(net_power, report_style='None')
        else:
            break
    # run powerflow
    pp.runpp(net_power)
        
    
    # hier fehlen dann noch Maßnahmen, um spannungs- und auslastungstoleranzen (grenzen) einzuhalten.
    # z.b. alle Trafos unter 100 prozent loading bringen. Dazu dann sgens,gens und load Knotendirekt verändern.
    # Das aber auch alles über das scaling, damit man die original werte noch hat
    
    # Evt. mit dem opf arbeiten und dann das max loading bei den betriebsmitteln direkt hinterlegen
    # Mal OPF Tutorial durchgehen
    # hierbei muss bei den loads, sgens und gens controllable definiert sein und deren grenzen
    # schaune ob ich das optimierte netz dann abspeichern kann
    

    return net_power