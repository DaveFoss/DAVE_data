"""
Hier eine funktion schreiben die alle modellierungsfunktionen so aufruft das aus einem Ortsnamen 
oder einer PLZ ein fertiges Netz für strom und gas rauskommt

Eingangsparameter müssten dann Ortsname, Bundeslandslame oder PLZ sein
"""


def create_grid(postalcode=None, town_name=None, federal_state=None, own_area=None,voltage_level='HV', pressure_level='HP'):
    
    """
    hier berücksichtigen das verschiedene Spannungsebenen, verschiedene funktionen benötigen
    Parameter voltage_level ist list of string mit allen SPannungsebeen die gewünsct sind ['HS','MS','NS']
    """
    # hier noch auswahl welchen eingangsparamter wir haben und parameter für das Netzgebiet über target_area funktion besorgen
    target=target_area(own_area=path)
    """
    if 'HV' is in voltage_level:
        pass
    if 'MV' is in voltage_level:
        pass
    if 'LV' is in voltage_level:
        pass
    if 'HP' is in pressure_level:
        pass
    if 'MP' is in pressure_level:
        pass
    if 'LP' is in pressure_level:
        pass
    """