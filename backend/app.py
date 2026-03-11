
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from optimization.energy_optimizer import optimize_energy
# from simulation.demand_loader import get_current_demand
# from ml.inference.predict_solar import predict_solar
# from backend.services.weather_services import get_weather_data

# from optimization.energy_storage import (
#     initialize_backup,
#     use_backup,
#     add_surplus,
#     get_backup
# )

# import pandas as pd


# app = FastAPI(title="AI Renewable Smart Grid API")

# # Allow frontend connections
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize backup energy using dataset
# initialize_backup()


# @app.get("/")
# def home():
#     return {
#         "status": "running",
#         "message": "AI Renewable Smart Grid API"
#     }


# @app.get("/smart-grid-status")
# def smart_grid_status():

#     try:

#         # 1️⃣ Get live weather
#         weather = get_weather_data()

#         irradiance = weather["solar_irradiance"]
#         temperature = weather["temperature"]
#         module_temp = temperature + 5

#         # 2️⃣ Predict solar generation
#         solar_generation = predict_solar(
#             irradiance,
#             temperature,
#             module_temp
#         )

#         # 3️⃣ Load city demand
#         demand = get_current_demand()

#         total_demand = sum(demand.values())

#         backup_used = 0

#         # 4️⃣ If solar insufficient → use backup energy
#         if solar_generation < total_demand:

#             deficit = total_demand - solar_generation

#             backup_used = use_backup(deficit)

#             solar_generation += backup_used

#         else:

#             # Store surplus energy
#             surplus = solar_generation - total_demand

#             add_surplus(surplus)

#         # 5️⃣ Optimize distribution
#         allocation = optimize_energy(
#             solar_generation,
#             demand
#         )

#         # 6️⃣ Grid metrics
#         energy_balance = solar_generation - total_demand

#         if total_demand > 0:
#             grid_stability = min(1, solar_generation / total_demand)
#         else:
#             grid_stability = 1

#         return {

#             "weather": weather,

#             "solar_generation": round(solar_generation, 2),

#             "total_demand": round(total_demand, 2),

#             "energy_balance": round(energy_balance, 2),

#             "grid_stability_score": round(grid_stability, 2),

#             "backup_used": round(backup_used, 2),

#             "backup_remaining": round(get_backup(), 2),

#             "demand": demand,

#             "optimized_distribution": allocation
#         }

#     except Exception as e:

#         return {
#             "status": "error",
#             "message": str(e)
#         }


# @app.get("/solar-forecast")
# def solar_forecast():

#     df = pd.read_csv("data/raw/amaravati_energy_dataset.csv")

#     forecast = []

#     for hour in range(24):

#         row = df.iloc[hour]

#         prediction = predict_solar(
#             row["solar_irradiance"],
#             row["temperature"],
#             row["temperature"] + 5
#         )

#         forecast.append({
#             "hour": hour,
#             "predicted_generation": round(prediction, 2)
#         })

#     return {
#         "forecast": forecast
#     }



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import asyncio

from optimization.energy_optimizer import optimize_energy
from simulation.demand_loader import get_current_demand
from ml.inference.predict_solar import predict_solar
from backend.services.weather_services import get_weather_data

from optimization.energy_storage import (
    initialize_backup,
    use_backup,
    add_surplus,
    get_backup
)

app = FastAPI(title="AI Renewable Smart Grid")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_backup()

latest_grid_state = {}


def run_grid_cycle():
    global latest_grid_state

    weather = get_weather_data()

    irradiance = weather["solar_irradiance"]
    temperature = weather["temperature"]

    solar_generation = predict_solar(
        irradiance,
        temperature,
        temperature + 5
    )

    demand = get_current_demand()

    total_demand = sum(demand.values())

    battery_before = get_backup()

    surplus_added = 0
    backup_used = 0
    battery_after = battery_before

    if solar_generation >= total_demand:

        surplus_added = solar_generation - total_demand
        battery_before, battery_after = add_surplus(surplus_added)
        available_energy = total_demand

    else:

        deficit = total_demand - solar_generation
        backup_used, battery_before, battery_after = use_backup(deficit)
        available_energy = solar_generation + backup_used

    allocation = optimize_energy(
        available_energy,
        demand
    )

    energy_balance = available_energy - total_demand

    grid_stability = min(1, available_energy / total_demand) if total_demand > 0 else 1

    latest_grid_state = {

        "weather": weather,

        "solar_generation": round(solar_generation, 2),

        "total_demand": round(total_demand, 2),

        "energy_balance": round(energy_balance, 2),

        "grid_stability_score": round(grid_stability, 2),

        "battery_before": round(battery_before, 2),

        "surplus_added_today": round(surplus_added, 2),

        "backup_used": round(backup_used, 2),

        "battery_after": round(battery_after, 2),

        "demand": demand,

        "optimized_distribution": allocation
    }


async def background_grid_loop():

    while True:

        run_grid_cycle()

        await asyncio.sleep(10)  # update every 10 seconds


@app.on_event("startup")
async def start_background_loop():

    asyncio.create_task(background_grid_loop())


@app.get("/")
def home():
    return {"message": "AI Renewable Smart Grid Running"}


@app.get("/smart-grid-status")
def smart_grid():
    return latest_grid_state


@app.get("/battery-history")
def battery_history():

    df = pd.read_csv("data/battery_log.csv")

    return df.to_dict(orient="records")

@app.get("/forecast-tomorrow")
def forecast_tomorrow():

    # get current weather
    weather = get_weather_data()

    irradiance = weather["solar_irradiance"]
    temperature = weather["temperature"]

    # predict tomorrow solar generation
    predicted_solar = predict_solar(
        irradiance,
        temperature,
        temperature + 5
    )

    demand = get_current_demand()

    total_demand = sum(demand.values())

    expected_energy_balance = predicted_solar - total_demand

    return {

        "tomorrow_weather_estimate": weather,

        "predicted_solar_generation": round(predicted_solar, 2),

        "expected_total_demand": round(total_demand, 2),

        "expected_energy_balance": round(expected_energy_balance, 2),

        "current_battery_level": round(get_backup(), 2)
    }