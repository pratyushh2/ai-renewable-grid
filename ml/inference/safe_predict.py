from ml.inference.predict_solar import predict_solar

def safe_predict_solar(irradiance, temperature, module_temp):

    try:
        power = predict_solar(irradiance, temperature, module_temp)

        if power < 0:
            power = 0

        return power

    except Exception as e:
        print("ML prediction failed:", e)

        # fallback physics estimate
        return irradiance * 0.20