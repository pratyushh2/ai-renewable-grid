import sys
import os

# allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from ml.inference.predict_solar import predict_solar
from backend.services.weather_services import get_weather_data


rows = []

weather = get_weather_data()

temperature = weather["temperature"]

start = datetime.now()

for hour in range(48):  # next 2 days

    timestamp = start + timedelta(hours=hour)

    h = timestamp.hour

    # simulate sunlight curve
    solar_factor = max(0, np.sin((h - 6) * np.pi / 12))

    irradiance = weather["solar_irradiance"] * solar_factor

    predicted_power = predict_solar(
        irradiance,
        temperature,
        temperature + 5
    )

    rows.append({
        "timestamp": timestamp,
        "solar_irradiance": round(irradiance,2),
        "temperature": temperature,
        "predicted_generation": round(predicted_power,2)
    })

df = pd.DataFrame(rows)

df.to_csv("data/energy_forecast.csv", index=False)

print("Energy forecast dataset generated")