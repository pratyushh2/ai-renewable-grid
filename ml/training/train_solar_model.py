import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

print("Loading datasets...")

generation = pd.read_csv("data/raw/Plant_1_Generation_Data.csv")
weather = pd.read_csv("data/raw/Plant_1_Weather_Sensor_Data.csv")

generation["DATE_TIME"] = pd.to_datetime(generation["DATE_TIME"], dayfirst=True)
weather["DATE_TIME"] = pd.to_datetime(weather["DATE_TIME"], dayfirst=True)

# Merge datasets
data = pd.merge(generation, weather, on="DATE_TIME")

# Feature selection
features = [
    "IRRADIATION",
    "AMBIENT_TEMPERATURE",
    "MODULE_TEMPERATURE"
]

target = "AC_POWER"

X = data[features]
y = data[target]

print("Splitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print("Training model...")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

print("Evaluating model...")

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("Mean Absolute Error:", mae)
print("R² Score:", r2)

print("Saving model...")

joblib.dump(model, "ml/models/solar_model.pkl")

print("Model trained and saved successfully!")