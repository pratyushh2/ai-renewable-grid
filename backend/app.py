
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
import hashlib
import random
from datetime import datetime
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

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

class ChatRequest(BaseModel):
    query: str

class SimulateRequest(BaseModel):
    solar_capacity: float
    battery_size: float
    cloud_cover: float
    city_demand: float

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
battery_soh_global = 92.4


def run_grid_cycle():
    global latest_grid_state, battery_soh_global

    weather = get_weather_data()

    irradiance = weather.get("solar_irradiance", 0)
    temperature = weather.get("temperature", 30)
    wind_speed = weather.get("wind_speed", 0)
    cloud_cover = weather.get("cloud_cover", 0)

    # 1. Storm Mode Intervention
    storm_mode = bool(wind_speed > 40 or cloud_cover > 90)

    predicted_solar = predict_solar(
        irradiance,
        temperature,
        temperature + 5
    )
    
    # 2. Solar Efficiency
    solar_efficiency = round(random.uniform(0.88, 0.95), 4)
    actual_solar = predicted_solar * solar_efficiency
    
    if storm_mode:
        actual_solar *= 0.2

    # 3. Smart Battery Dispatch & 4. Battery SoH
    smart_dispatch_active = bool(cloud_cover > 50 and not storm_mode)
    battery_soh_global = max(70.0, battery_soh_global - 0.001)

    demand = get_current_demand()

    total_demand = sum(demand.values())

    battery_before = get_backup()

    surplus_added = 0
    backup_used = 0
    v2g_supplied = 0
    battery_after = battery_before

    if actual_solar >= total_demand:
        surplus_added = actual_solar - total_demand
        battery_before, battery_after = add_surplus(surplus_added)
        available_energy = total_demand
    else:
        deficit = total_demand - actual_solar
        if storm_mode:
            deficit_allowed = min(deficit, battery_before * 0.1)
        else:
            deficit_allowed = deficit
            
        backup_used, battery_before, battery_after = use_backup(deficit_allowed)
        available_energy = actual_solar + backup_used
        
        # 5. V2G Simulation
        remaining_deficit = total_demand - available_energy
        if remaining_deficit > 0:
            v2g_max = 3.0
            v2g_supplied = min(v2g_max, remaining_deficit)
            available_energy += v2g_supplied

    allocation = optimize_energy(
        available_energy,
        demand
    )

    energy_balance = available_energy - total_demand

    grid_stability = min(1.0, available_energy / total_demand) if total_demand > 0 else 1.0

    # 8. Data Integrity Hash
    raw_str = f"{actual_solar}-{total_demand}-{available_energy}-{datetime.now().timestamp()}"
    audit_hash = hashlib.sha256(raw_str.encode()).hexdigest()

    latest_grid_state = {
        "weather": weather,
        "solar_generation": round(actual_solar, 2),
        "total_demand": round(total_demand, 2),
        "energy_balance": round(energy_balance, 2),
        "grid_stability_score": round(grid_stability, 2),
        "battery_before": round(battery_before, 2),
        "surplus_added_today": round(surplus_added, 2),
        "backup_used": round(backup_used, 2),
        "battery_after": round(battery_after, 2),
        "demand": demand,
        "optimized_distribution": allocation,
        
        "storm_mode_active": storm_mode,
        "solar_efficiency_pct": round(solar_efficiency * 100, 2),
        "smart_dispatch_active": smart_dispatch_active,
        "battery_soh": round(battery_soh_global, 2),
        "v2g_supplied": round(v2g_supplied, 2),
        "latest_audit_hash": audit_hash
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

@app.get("/report")
def generate_report():
    data = latest_grid_state
    if not data:
        return {"error": "No data yet"}
    
    csv_rows = []
    csv_rows.append("SmartGrid OS - Daily Performance Report")
    csv_rows.append(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    csv_rows.append("")
    csv_rows.append("Metric,Value")
    csv_rows.append(f"Solar Generated (MW),{data.get('solar_generation')}")
    csv_rows.append(f"Total Demand (MW),{data.get('total_demand')}")
    csv_rows.append(f"Energy Balance (MW),{data.get('energy_balance')}")
    csv_rows.append(f"Grid Stability (%),{data.get('grid_stability_score', 0) * 100}")
    csv_rows.append(f"Battery Level (MWh),{data.get('battery_after') / 80 * 100}%")
    csv_rows.append("")
    csv_rows.append("Zone,Demand (MW),Allocated (MW)")
    
    order = ['Assembly', 'Government Offices', 'Capital Complex', 'Residential', 'Solar Farm']
    for zone in order:
        demand = data.get("demand", {}).get(zone, 0)
        alloc = data.get("optimized_distribution", {}).get(zone, 0)
        csv_rows.append(f"{zone},{demand},{alloc}")
        
    csv_content = "\\n".join(csv_rows)
    return PlainTextResponse(
        content=csv_content,
        headers={"Content-Disposition": "attachment; filename=SmartGrid_Report.csv"}
    )

@app.post("/simulate")
def simulate_grid(req: SimulateRequest):
    solar_gen = req.solar_capacity * (1 - ((req.cloud_cover / 100) * 0.80))
    shortage = req.city_demand - solar_gen
    
    if shortage <= 0:
        actual_supplied = req.city_demand
        bat_status = "Charging"
    else:
        if req.battery_size >= shortage:
            bat_status = "Discharging"
            actual_supplied = req.city_demand
        else:
            bat_status = "Exhausted"
            actual_supplied = solar_gen + req.battery_size
            
    stability = min(1.0, actual_supplied / req.city_demand) * 100
    balance = actual_supplied - req.city_demand
    
    return {
        "stability": round(stability, 1),
        "solar_gen": round(solar_gen, 1),
        "balance": round(balance, 1),
        "bat_status": bat_status,
        "actual_supplied": round(actual_supplied, 1)
    }

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    query = req.query.lower()
    state = latest_grid_state
    if not state:
        return {"response": "System still initializing. Please wait."}
        
    if "shortage" in query or "unmet" in query or "deficit" in query or "enough" in query:
        shortage = state["total_demand"] - (state["solar_generation"] + state["backup_used"])
        if shortage <= 0:
            return {"response": f"There is currently no energy shortage. We are generating {state['solar_generation']} MW of solar power, fully meeting the {state['total_demand']} MW demand."}
        else:
            return {"response": f"We are currently facing a {shortage:.1f} MW shortfall. The cloud cover is at {state['weather'].get('cloud_cover')}% which is reducing solar output."}
            
    if "ev " in query or "curtail" in query or "cut" in query or "hospital" in query or "assembly" in query or "solar" in query:
        ev_alloc = state["optimized_distribution"].get("Solar Farm", 0)
        ev_demand = state["demand"].get("Solar Farm", 0)
        if ev_alloc < ev_demand:
            return {"response": f"Solar Farm (lowest priority) is currently curtailed (receiving {ev_alloc} of {ev_demand} MW)."}
        else:
            return {"response": f"All zones including Solar Farm are fully powered right now!"}
            
    if "battery" in query or "storage" in query or "charge" in query:
        pct = (state["battery_after"] / 80) * 100
        if state["surplus_added_today"] > 0:
            return {"response": f"Battery is CHARGING with surplus {state['surplus_added_today']} MW. Level: {pct:.1f}%"}
        elif state["backup_used"] > 0:
            return {"response": f"Battery is DISCHARGING {state['backup_used']} MW. Level: {pct:.1f}%"}
        else:
            return {"response": f"Battery HOLDING at {pct:.1f}%."}
            
    if "optimiz" in query or "strategy" in query or "algorithm" in query:
        return {"response": f"My optimization strategy protects critical infrastructure first."}
        
    if "status" in query or "health" in query or "overall" in query:
        return {"response": f"Grid stability is {state['grid_stability_score']*100}%. Weather: {state['weather'].get('temperature')}°C."}
        
    if "weather" in query or "cloud" in query or "sun" in query:
        return {"response": f"Currently {state['weather'].get('temperature')}°C with {state['weather'].get('cloud_cover')}% cloud cover. Generating {state['solar_generation']} MW."}
        
    if "why is" in query and ("degraded" in query or "critical" in query):
        shortage = state["total_demand"] - (state["solar_generation"] + state["backup_used"])
        if shortage <= 0: return {"response": "The grid is STABLE right now."}
        return {"response": f"Demand exceeds supply by {shortage:.1f} MW. Battery is pushing {state['backup_used']} MW but it's not enough."}
        
    if "run" in query and "optimiz" in query:
        return {"response": "Running forced optimization cycle... Audit Hash stored."}
        
    if "explain" in query and ("allocation" in query or "energy" in query):
        return {"response": "Energy is routed to Assembly and Govt Offices first..."}
        
    return {"response": "I analyze the live grid. Ask me about grid stability, battery, or optimization."}