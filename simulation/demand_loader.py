# import pandas as pd

# DATASET_PATH = "data/raw/amaravati_energy_dataset.csv"

# def get_current_demand():

#     df = pd.read_csv(DATASET_PATH)

#     latest = df.tail(5)

#     demand = {}

#     for _, row in latest.iterrows():
#         demand[row["zone"]] = row["demand_MW"]

#     return demand

import pandas as pd
import os

DATASET_PATH = "data/raw/amaravati_energy_dataset.csv"

def get_current_demand():

    try:

        df = pd.read_csv(DATASET_PATH)

    except FileNotFoundError:

        print("Dataset not found. Generating fallback demand.")

        zones = [
            "Assembly",
            "Government Offices",
            "Capital Complex",
            "Residential",
            "Solar Farm"
        ]

        return {zone: 30 for zone in zones}

    latest = df.tail(5)

    demand = {}

    for _, row in latest.iterrows():
        demand[row["zone"]] = row["demand_MW"]

    return demand