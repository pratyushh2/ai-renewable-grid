from fastapi import FastAPI
from pydantic import BaseModel
from ml.inference.predict_solar import predict_solar

app = FastAPI()

class SolarInput(BaseModel):
    irradiation: float
    temperature: float
    module_temp: float


@app.post("/predict-solar")
def predict(data: SolarInput):

    power = predict_solar(
        data.irradiation,
        data.temperature,
        data.module_temp
    )

    return {
        "predicted_solar_power": power
    }