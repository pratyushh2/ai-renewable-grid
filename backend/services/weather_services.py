# import requests

# LAT = 16.5062
# LON = 80.6480

# def get_weather_data():
#     url = (
#         "https://api.open-meteo.com/v1/forecast"
#         f"?latitude={LAT}"
#         f"&longitude={LON}"
#         "&current=temperature_2m,cloud_cover,wind_speed_10m,shortwave_radiation"
#     )

#     response = requests.get(url)
#     data = response.json()

#     current = data["current"]

#     weather_data = {
#         "temperature": current["temperature_2m"],
#         "solar_irradiance": current["shortwave_radiation"],
#         "cloud_cover": current["cloud_cover"],
#         "wind_speed": current["wind_speed_10m"]
#     }

#     return weather_data


# if __name__ == "__main__":
#     print(get_weather_data())

# import requests

# LAT = 16.5062
# LON = 80.6480

# def get_weather_data():

#     try:

#         url = (
#             "https://api.open-meteo.com/v1/forecast"
#             f"?latitude={LAT}"
#             f"&longitude={LON}"
#             "&current=temperature_2m,cloud_cover,wind_speed_10m,shortwave_radiation"
#         )

#         response = requests.get(url, timeout=5)

#         data = response.json()

#         current = data["current"]

#         return {
#             "temperature": current["temperature_2m"],
#             "solar_irradiance": current["shortwave_radiation"],
#             "cloud_cover": current["cloud_cover"],
#             "wind_speed": current["wind_speed_10m"]
#         }

#     except Exception as e:

#         print("Weather API failed:", e)

#         # fallback values
#         return {
#             "temperature": 30,
#             "solar_irradiance": 600,
#             "cloud_cover": 20,
#             "wind_speed": 3
#         }

import requests

LAT = 16.5062
LON = 80.6480


def get_weather_data():

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}"
        f"&longitude={LON}"
        "&current=temperature_2m,cloud_cover,wind_speed_10m,shortwave_radiation"
    )

    try:

        response = requests.get(url, timeout=8)

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        weather_data = {
            "temperature": current["temperature_2m"],
            "solar_irradiance": current["shortwave_radiation"],
            "cloud_cover": current["cloud_cover"],
            "wind_speed": current["wind_speed_10m"]
        }

        print("LIVE WEATHER:", weather_data)

        return weather_data

    except Exception as e:

        print("Weather API failed, using fallback:", e)

        # Fake values ONLY when API fails
        return {
            "temperature": 30,
            "solar_irradiance": 600,
            "cloud_cover": 20,
            "wind_speed": 3
        }