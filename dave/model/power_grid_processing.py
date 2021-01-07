import pandapower as pp


def power_processing(net, opt_model, min_vm_pu=0.95, max_vm_pu=1.05, max_line_loading=100,
                     max_trafo_loading=100):
    """
    This function run a diagnosis of the pandapower network and clean up occurring failures.
    Furthermore the grid will be adapt so all boundarys be respected.

    INPUT:
        **net** (attrdict) - pandapower attrdict

    OUTPUT:
        **net** (attrdict) - A cleaned up and if necessary optimized pandapower attrdict
    """
    print('run power grid diagnostic and processing')
    print('----------------------------------------')
    # run network diagnostic
    diagnostic = pp.diagnostic(net, report_style='None')
    # --- clean up failures detected by the diagnostic tool
    # delete disconected buses and the elements connected to them
    if 'disconnected_elements' in diagnostic.keys():
        for idx in range(0, len(diagnostic['disconnected_elements'])):
            drop_buses = diagnostic['disconnected_elements'][idx]['buses']
            pp.drop_buses(net, drop_buses)
    # run network diagnostic
    diagnostic = pp.diagnostic(net, report_style='None')
    # change lines with impedance close to zero to switches
    if 'impedance_values_close_to_zero' in diagnostic.keys():
        lines = diagnostic['impedance_values_close_to_zero'][0]['line']
        for line_index in lines:
            pp.create_replacement_switch_for_branch(net, element='line', idx=line_index)
        pp.drop_lines(net, lines=lines)
    # run network diagnostic
    diagnostic = pp.diagnostic(net, report_style='None')
    # correct invalid values
    if 'invalid_values' in diagnostic.keys():
        if 'gen' in diagnostic['invalid_values'].keys():
            for gen in diagnostic['invalid_values']['gen']:
                if (gen[1] == 'p_mw') and (gen[2] == 'nan'):
                    net.gen.at[gen[0], 'p_mw'] = 0
        if 'line' in diagnostic['invalid_values'].keys():
            drop_lines = []
            for line in diagnostic['invalid_values']['line']:
                if (line[1] == 'length_km') and (line[2] == 0):
                    pp.create_replacement_switch_for_branch(net, element='line', idx=line[0])
                    drop_lines.append(line[0])
            pp.drop_lines(net, lines=drop_lines)
    # delete parallel switches
    diagnostic = pp.diagnostic(net, report_style='None')
    if 'parallel_switches' in diagnostic.keys():
        for i in range(0, len(diagnostic['parallel_switches'])):
            parallel_switches = diagnostic['parallel_switches'][i]
            # keep the first switch and delete the other ones
            for j in range(1, len(parallel_switches)):
                net.switch = net.switch.drop([parallel_switches[j]])

    # --- optimize grid model
    if opt_model:
        print('run power grid optimization')
        print('---------------------------')
        # run network diagnostic
        diagnostic = pp.diagnostic(net, report_style='None')
        # clean up overloads
        while 'overload' in diagnostic.keys():
            if (diagnostic['overload']['generation']) and (net.sgen.scaling.min() >= 0.1):
                # scale down sgens about 10%
                net.sgen.scaling -= 0.1
                # run diagnostic after scale down for a new report
                diagnostic = pp.diagnostic(net, report_style='None')
            elif (diagnostic['overload']['load']) and (net.load.scaling.min() >= 0.1):
                # scale down sgens about 10%
                net.load.scaling -= 0.1
                # run diagnostic after scale down for a new report
                diagnostic = pp.diagnostic(net, report_style='None')
            else:
                break
        # check if pf converged and there are no violations, otherwise must use opf
        try:
            # run powerflow
            pp.runpp(net, max_iteration=100)
            pf_converged = True
            # check boundarys
            if net.res_bus.vm_pu.min() < min_vm_pu:
                use_opf = True
                min_vm_pu_pf = net.res_bus.vm_pu.min()
            elif net.res_bus.vm_pu.max() > max_vm_pu:
                use_opf = True
                max_vm_pu_pf = net.res_bus.vm_pu.max()
            elif net.res_line.loading_percent.max() > max_line_loading:
                use_opf = True
                max_line_loading_pf = net.res_line.loading_percent.max()
            elif net.res_trafo.loading_percent.max() > max_trafo_loading:
                use_opf = True
                max_trafo_loading_pf = net.res_trafo.loading_percent.max()
            else:
                use_opf = False
                print('power flow converged and has no violations')
        except:
            use_opf = True
            pf_converged = False
            print('power flow did not converged')
        # optimize grid with opf
        if use_opf:
            # --- try opf to find optimized network to network constraints
            # set grid parameter boundrys
            net.bus['min_vm_pu'] = min_vm_pu
            net.bus['max_vm_pu'] = max_vm_pu
            net.line['max_loading_percent'] = max_line_loading
            net.trafo['max_loading_percent'] = max_trafo_loading
            # set flexibilities
            # for loads
            net.load['min_p_mw'] = 0
            net.load['max_p_mw'] = net.load.p_mw
            net.load['min_q_mvar'] = 0
            net.load['max_q_mvar'] = net.load.q_mvar
            net.load['controllable'] = True
            # for sgens
            net.sgen['min_p_mw'] = 0
            net.sgen['max_p_mw'] = net.sgen.p_mw
            net.sgen['min_q_mvar'] = 0
            net.sgen['max_q_mvar'] = 0
            net.sgen['controllable'] = True
            # for gens
            net.gen['min_vm_pu'] = min_vm_pu  # necessary for OPF
            net.gen['max_vm_pu'] = max_vm_pu  # necessary for OPF
            net.gen['min_p_mw'] = 0
            net.gen['max_p_mw'] = net.gen.p_mw
            #net.gen['min_q_mvar']
            #net.gen['max_q_mvar']
            net.gen['controllable'] = True
            # check if opf converged and the results are better as before
            try:
                # run optimal power flow
                pp.runopp(net, verbose=True)
                # check results and compare with previous parameters
                if pf_converged:
                    min_bus = ((net.res_bus.vm_pu.min() > min_vm_pu_pf) or
                               (net.res_bus.vm_pu.min() > min_vm_pu))
                    max_bus = ((net.res_bus.vm_pu.max() < max_vm_pu_pf) or
                               (net.res_bus.vm_pu.max() < max_vm_pu))
                    max_line = ((net.res_line.loading_percent.max() < max_line_loading_pf) or
                                (net.res_line.loading_percent.max() < max_line_loading))
                    max_trafo = ((net.res_trafo.loading_percent.max() < max_trafo_loading_pf) or
                                 (net.res_trafo.loading_percent.max() < max_trafo_loading))
                if (not pf_converged) or (min_bus and max_bus and max_line and max_trafo):
                    # save original parameters as installed power in grid model
                    net.sgen['p_mw_installed'] = net.sgen.p_mw
                    net.sgen['q_mvar_installed'] = net.sgen.q_mvar
                    net.load['p_mw_installed'] = net.load.p_mw
                    net.load['q_mvar_installed'] = net.load.q_mvar
                    net.gen['p_mw_installed'] = net.gen.p_mw
                    net.gen['sn_mva_installed'] = net.gen.sn_mva
                    net.gen['vm_pu_installed'] = net.gen.vm_pu
                    # set grid parameters to the calculated ones from the opf
                    net.sgen.p_mw = net.res_sgen.p_mw
                    net.sgen.q_mvar = net.res_sgen.q_mvar
                    net.load.p_mw = net.res_load.p_mw
                    net.load.q_mvar = net.res_load.q_mvar
                    net.gen.p_mw = net.res_gen.p_mw
                    net.gen.sn_mva = (net.res_gen.p_mw**2 + net.res_gen.q_mvar**2).pow(1/2)
                    net.gen.vm_pu = net.res_gen.vm_pu
            except:
                print('optimal power flow did not converged')
        # print results for boundaries parameters
        print('the optimized grid modell has the following charakteristik:')
        print(f'min_vm_pu: {net.res_bus.vm_pu.min()}')
        print(f'max_vm_pu: {net.res_bus.vm_pu.max()}')
        print(f'max_line_loading: {net.res_line.loading_percent.max()}')
        print(f'max_trafo_loading: {net.res_trafo.loading_percent.max()}')
    return net
