# import joblib
# import pandas as pd

# # Load trained model
# model = joblib.load("ml/models/solar_model.pkl")


# def predict_solar(irradiation, ambient_temp, module_temp):

#     data = pd.DataFrame([{
#         "IRRADIATION": irradiation,
#         "AMBIENT_TEMPERATURE": ambient_temp,
#         "MODULE_TEMPERATURE": module_temp
#     }])

#     prediction = model.predict(data)

#     return float(prediction[0])


# if __name__ == "__main__":

#     # Test example
#     power = predict_solar(
#         irradiation=850,
#         ambient_temp=32,
#         module_temp=45
#     )

#     print("Predicted Solar Power:", power)

import joblib
from ml.utils.feature_builder import build_features

MODEL_PATH = "ml/models/solar_model.pkl"

model = joblib.load(MODEL_PATH)

def predict_solar(irradiation, ambient_temp, module_temp):
    features = build_features(
        irradiation,
        ambient_temp,
        module_temp
    )

    prediction = model.predict(features)

    return float(prediction[0])


if __name__ == "__main__":

    power = predict_solar(
        irradiation=900,
        ambient_temp=33,
        module_temp=47
    )

    print("Predicted Solar Power:", power)