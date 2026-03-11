# import pandas as pd

# DATASET = "data/raw/amaravati_energy_dataset.csv"

# backup_energy = 0


# def initialize_backup():

#     global backup_energy

#     df = pd.read_csv(DATASET)

#     avg_irradiance = df["solar_irradiance"].mean()

#     backup_energy = avg_irradiance * 10


# def use_backup(required):

#     global backup_energy

#     if backup_energy <= 0:
#         return 0

#     used = min(required, backup_energy)

#     backup_energy -= used

#     return used


# def add_surplus(amount):

#     global backup_energy

#     backup_energy += amount


# def get_backup():

#     return backup_energy

# import pandas as pd
# from datetime import datetime
# import os

# # Initial battery storage
# backup_energy = 500

# LOG_FILE = "data/battery_log.csv"


# def initialize_backup():
#     global backup_energy
#     return backup_energy


# def get_backup():
#     return backup_energy


# def use_backup(required):

#     global backup_energy

#     battery_before = backup_energy

#     used = min(required, backup_energy)

#     backup_energy -= used

#     battery_after = backup_energy

#     log_battery(-used, battery_after)

#     return used, battery_before, battery_after


# def add_surplus(amount):

#     global backup_energy

#     battery_before = backup_energy

#     if amount > 0:
#         backup_energy += amount

#     battery_after = backup_energy

#     log_battery(amount, battery_after)

#     return battery_before, battery_after


# def log_battery(change, battery_level):

#     row = {
#         "timestamp": datetime.now(),
#         "energy_change": round(change, 2),
#         "battery_level": round(battery_level, 2)
#     }

#     df = pd.DataFrame([row])

#     if os.path.exists(LOG_FILE):
#         df.to_csv(LOG_FILE, mode="a", header=False, index=False)
#     else:
#         df.to_csv(LOG_FILE, index=False)



import pandas as pd
import os
from datetime import datetime

battery_energy = 500

LOG_FILE = "data/battery_log.csv"

MAX_LOGS = 300


def initialize_backup():
    global battery_energy
    return battery_energy


def get_backup():
    global battery_energy
    return battery_energy


def use_backup(required):

    global battery_energy

    battery_before = battery_energy

    used = min(required, battery_energy)

    battery_energy -= used

    battery_after = battery_energy

    log_battery(-used, battery_after)

    return used, battery_before, battery_after


def add_surplus(amount):

    global battery_energy

    battery_before = battery_energy

    if amount > 0:
        battery_energy += amount

    battery_after = battery_energy

    log_battery(amount, battery_after)

    return battery_before, battery_after


def log_battery(change, battery_level):

    row = {
        "timestamp": datetime.now(),
        "energy_change": round(change, 2),
        "battery_level": round(battery_level, 2)
    }

    df_new = pd.DataFrame([row])

    if os.path.exists(LOG_FILE):

        df = pd.read_csv(LOG_FILE)

        df = pd.concat([df, df_new], ignore_index=True)

        if len(df) > MAX_LOGS:
            df = df.tail(MAX_LOGS)

        df.to_csv(LOG_FILE, index=False)

    else:

        df_new.to_csv(LOG_FILE, index=False)