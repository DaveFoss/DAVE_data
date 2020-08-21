# --- DaVe Settings for assumptions and used data versions

def dave_settings():
    settings = {# OEP versions:
                'hv_buses_ver':    'version=v0.4.6',
                'hv_line_ver':     'version=v0.4.6',
                'ehv_sub_ver':     'version=v0.4.5',
                'ehvhv_trans_ver': 'version=v0.4.6',
                'hvmv_sub_ver':    'version=v0.4.5',
                'mvlv_sub_ver':    'version=v0.4.5'
                # assumptions at grid generating:
                # assumptions at pandapower convert:
                
                }
    
    
    return settings