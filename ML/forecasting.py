import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================
# 1. LOAD DATA
# ============================================

df = pd.read_csv("patient_data.csv")

df["Admission_Date"] = pd.to_datetime(df["Admission_Date"])


# ============================================
# 2. CREATE DAILY TIME SERIES
# ============================================

daily = (
    df.groupby(df["Admission_Date"].dt.date)
      .size()
      .reset_index(name="Admissions")
)

daily["Admission_Date"] = pd.to_datetime(daily["Admission_Date"])

daily = (
    daily.sort_values("Admission_Date")
         .set_index("Admission_Date")
         .asfreq("D", fill_value=0)
         .reset_index()
)


# ============================================
# 3. CREATE FORECASTING FEATURES
# ============================================

daily["Lag_1"] = daily["Admissions"].shift(1)
daily["Lag_7"] = daily["Admissions"].shift(7)

daily["Rolling_3"] = (
    daily["Admissions"]
    .shift(1)
    .rolling(3)
    .mean()
)

daily["Rolling_7"] = (
    daily["Admissions"]
    .shift(1)
    .rolling(7)
    .mean()
)

daily["Day_of_Week"] = daily["Admission_Date"].dt.dayofweek


# Remove rows where lag information isn't available
model_data = daily.dropna().reset_index(drop=True)


print("\nModel dataset:")
print(model_data)


# ============================================
# 4. DEFINE FEATURES AND TARGET
# ============================================

features = [
    "Lag_1",
    "Lag_7",
    "Rolling_3",
    "Rolling_7",
    "Day_of_Week"
]

X = model_data[features]
y = model_data["Admissions"]


# ============================================
# 5. CHRONOLOGICAL TRAIN/TEST SPLIT
# ============================================

split = int(len(model_data) * 0.75)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================
# 6. TRAIN MODEL
# ============================================

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=4,
    random_state=42
)

model.fit(X_train, y_train)


# ============================================
# 7. PREDICT TEST DATA
# ============================================

predictions = model.predict(X_test)

predictions = np.maximum(predictions, 0)


# ============================================
# 8. EVALUATE
# ============================================

mae = mean_absolute_error(y_test, predictions)

rmse = np.sqrt(
    mean_squared_error(y_test, predictions)
)


print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print("MAE :", round(mae, 2))
print("RMSE:", round(rmse, 2))


# ============================================
# 9. ACTUAL VS PREDICTED
# ============================================

results = pd.DataFrame({
    "Date": model_data["Admission_Date"].iloc[split:].values,
    "Actual": y_test.values,
    "Predicted": np.round(predictions, 2)
})

print("\nActual vs Predicted:")
print(results)

# ============================================
# 10. FORECAST NEXT 7 DAYS
# ============================================

history = daily[["Admission_Date", "Admissions"]].copy()

future_predictions = []

for i in range(7):

    next_date = history["Admission_Date"].iloc[-1] + pd.Timedelta(days=1)

    lag_1 = history["Admissions"].iloc[-1]

    lag_7 = history["Admissions"].iloc[-7]

    rolling_3 = history["Admissions"].iloc[-3:].mean()

    rolling_7 = history["Admissions"].iloc[-7:].mean()

    day_of_week = next_date.dayofweek

    future_features = pd.DataFrame({
        "Lag_1": [lag_1],
        "Lag_7": [lag_7],
        "Rolling_3": [rolling_3],
        "Rolling_7": [rolling_7],
        "Day_of_Week": [day_of_week]
    })

    prediction = model.predict(future_features)[0]

    prediction = max(0, prediction)

    future_predictions.append({
        "Date": next_date,
        "Predicted_Admissions": round(prediction, 2)
    })

    # Add prediction to history so it can be used
    # for predicting the following day
    history = pd.concat([
        history,
        pd.DataFrame({
            "Admission_Date": [next_date],
            "Admissions": [prediction]
        })
    ], ignore_index=True)


forecast = pd.DataFrame(future_predictions)

print("\n==============================")
print("NEXT 7 DAYS FORECAST")
print("==============================")

print(forecast)

forecast.to_csv("forecast.csv", index=False)

print("\nForecast saved to forecast.csv")