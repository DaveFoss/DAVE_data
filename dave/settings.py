# DaVe Settings for assumptions and used data versions

def dave_settings():
    settings = {# --- data request
                # OEP versions:
                'hv_buses_ver':    'version=v0.4.6',
                'hv_line_ver':     'version=v0.4.6',
                'ehv_sub_ver':     'version=v0.4.5',
                'ehvhv_trans_ver': 'version=v0.4.6',
                'hvmv_sub_ver':    'version=v0.4.5',
                'mvlv_sub_ver':    'version=v0.4.5',
                # osm time delay (because osm doesn't alowed more than 1 request per second)
                'osm_time_delay': 60,  # in seconds
                
                # --- assumptions at grid generating:
                # mv level
                'mv_voltage': 20,
                # hours per year
                'h_per_a': 8760,
                # power factors for loads
                'cos_phi_residential': 0.95,  # induktiv
                'cos_phi_industrial':  0.75,  # induktiv
                'cos_phi_commercial':  0.75 , # induktiv
                # avarage load values for ehv, hv, and mv loads
                'residential_load': 2,  # in MW/km²
                'industrial_load': 10,  # in MW/km²
                'commercial_load':  3,  # in MW/km²
                
                # --- assumptions at pandapower convert:
                # lines standard types
                'lv_line_std_type': 'NAYY 4x150 SE',  # dummy value, must be changed
                # trafo parameters for ehv/ehv and  ehv/hv
                'trafo_vkr_percent': 0,  # dummy value
                'trafo_vk_percent': 10,  # dummy value
                'trafo_pfe_kw':      0,  # dummy value accepted as ideal
                'trafo_i0_percent':  0,  # dummy value accepted as ideal
                # trafo standard types
                'hvmv_trafo_std_type': '63 MVA 110/20 kV',  # dummy value, must be changed
                'mvlv_trafo_std_type': '0.63 MVA 20/0.4 kV',  # dummy value, must be changed
                }
    return settings