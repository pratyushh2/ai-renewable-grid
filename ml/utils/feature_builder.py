import pandas as pd

def build_features(irradiation, ambient_temp, module_temp):
    data = pd.DataFrame({
        "IRRADIATION": [irradiation],
        "AMBIENT_TEMPERATURE": [ambient_temp],
        "MODULE_TEMPERATURE": [module_temp]
    })

    return data