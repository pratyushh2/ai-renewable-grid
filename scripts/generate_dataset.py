# import sys
# import os

# # Allow script to access project root modules
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# from backend.services.weather_services import get_weather_data


# # Smart grid zones
# ZONES = [
#     "Assembly",
#     "Government Offices",
#     "Capital Complex",
#     "Residential",
#     "Solar Farm"
# ]

# rows = []

# start = datetime.now()

# print("Fetching real weather data...")

# # Fetch weather ONLY ONCE
# try:
#     weather = get_weather_data()
# except:
#     print("Weather API failed. Using fallback values.")
#     weather = {
#         "temperature": 30,
#         "solar_irradiance": 750,
#         "cloud_cover": 20,
#         "wind_speed": 3
#     }

# print("Weather Data:", weather)


# # Generate 7 days of hourly data
# for day in range(7):

#     for hour in range(24):

#         timestamp = start + timedelta(days=day, hours=hour)

#         # Simulate solar generation curve
#         solar_factor = max(0, np.sin((hour - 6) * np.pi / 12))
#         solar_generation = weather["solar_irradiance"] * solar_factor

#         for zone in ZONES:

#             base_demand = np.random.uniform(20, 50)

#             # Zone demand behavior
#             if zone == "Residential" and 18 <= hour <= 22:
#                 demand = base_demand + 25

#             elif zone == "Government Offices" and 9 <= hour <= 18:
#                 demand = base_demand + 20

#             elif zone == "Assembly" and 10 <= hour <= 16:
#                 demand = base_demand + 15

#             elif zone == "Capital Complex":
#                 demand = base_demand + 10

#             else:
#                 demand = base_demand

#             row = {
#                 "timestamp": timestamp,
#                 "hour": hour,
#                 "zone": zone,
#                 "temperature": weather["temperature"],
#                 "solar_irradiance": round(solar_generation, 2),
#                 "cloud_cover": weather["cloud_cover"],
#                 "wind_speed": weather["wind_speed"],
#                 "demand_MW": round(demand, 2)
#             }

#             rows.append(row)


# # Create DataFrame
# df = pd.DataFrame(rows)


# # Ensure directory exists
# os.makedirs("data/raw", exist_ok=True)


# # Save dataset
# output_path = "data/raw/amaravati_energy_dataset.csv"
# df.to_csv(output_path, index=False)

# print("\nDataset generated successfully!")
# print("Rows generated:", len(df))
# print("Saved to:", output_path)

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.weather_services import get_weather_data


ZONES = [
    "Assembly",
    "Government Offices",
    "Capital Complex",
    "Residential",
    "Solar Farm"
]


DATA_PATH = "data/raw/amaravati_energy_dataset.csv"


def generate_dataset(days):

    rows = []
    start = datetime.now()

    weather = get_weather_data()

    print("Weather Data:", weather)

    for day in range(days):

        for hour in range(24):

            timestamp = start + timedelta(days=day, hours=hour)

            # solar curve
            solar_factor = max(0, np.sin((hour - 6) * np.pi / 12))
            solar_generation = weather["solar_irradiance"] * solar_factor

            for zone in ZONES:

                base_demand = np.random.uniform(20, 50)

                if zone == "Residential" and 18 <= hour <= 22:
                    demand = base_demand + 25

                elif zone == "Government Offices" and 9 <= hour <= 18:
                    demand = base_demand + 20

                elif zone == "Assembly" and 10 <= hour <= 16:
                    demand = base_demand + 15

                elif zone == "Capital Complex":
                    demand = base_demand + 10

                else:
                    demand = base_demand

                rows.append({
                    "timestamp": timestamp,
                    "hour": hour,
                    "zone": zone,
                    "temperature": weather["temperature"],
                    "solar_irradiance": round(solar_generation,2),
                    "cloud_cover": weather["cloud_cover"],
                    "wind_speed": weather["wind_speed"],
                    "demand_MW": round(demand,2)
                })

    return pd.DataFrame(rows)


def save_dataset(df):

    os.makedirs("data/raw", exist_ok=True)

    df.to_csv(DATA_PATH, index=False)

    print("Dataset saved:", DATA_PATH)
    print("Rows:", len(df))


def fallback_simulation():

    print("Using simulated fallback dataset")

    rows = []

    for hour in range(24):

        for zone in ZONES:

            rows.append({
                "timestamp": datetime.now(),
                "hour": hour,
                "zone": zone,
                "temperature": 30,
                "solar_irradiance": 500,
                "cloud_cover": 20,
                "wind_speed": 3,
                "demand_MW": np.random.uniform(20,40)
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":

    try:

        print("Attempting 7-day dataset generation")

        df = generate_dataset(7)

        save_dataset(df)

    except Exception as e:

        print("7-day generation failed:", e)

        try:

            print("Falling back to 1-day dataset")

            df = generate_dataset(1)

            save_dataset(df)

        except Exception as e:

            print("1-day generation failed:", e)

            df = fallback_simulation()

            save_dataset(df)

    print("Dataset pipeline completed successfully")