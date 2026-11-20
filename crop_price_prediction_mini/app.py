import streamlit as st
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from pathlib import Path

st.set_page_config(page_title="Crop Price AI", page_icon="🌾", layout="wide")
DATA_PATH = Path(__file__).parent / "data" / "demo_crop_prices.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

@st.cache_resource
def train_model(df):
    features = ["crop", "market", "month", "price_lag_1", "price_avg_7",
                "arrivals", "rainfall_mm", "temperature_c", "humidity"]
    X = df[features].copy()
    y = df["modal_price"].astype(float)
    cat = ["crop", "market"]
    num = [c for c in features if c not in cat]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("num", "passthrough", num)
    ])
    model = Pipeline([
        ("prep", pre),
        ("xgb", XGBRegressor(
            n_estimators=180, max_depth=4, learning_rate=0.045,
            subsample=0.9, colsample_bytree=0.9, objective="reg:squarederror",
            random_state=42, n_jobs=2
        ))
    ])
    # Chronological split: last 20% is held out for a basic demo evaluation.
    split = int(len(df) * 0.8)
    model.fit(X.iloc[:split], y.iloc[:split])
    pred = model.predict(X.iloc[split:])
    metrics = {
        "MAE": mean_absolute_error(y.iloc[split:], pred),
        "RMSE": np.sqrt(mean_squared_error(y.iloc[split:], pred)),
        "R2": r2_score(y.iloc[split:], pred)
    }
    return model, features, metrics

def make_features(df, crop, market, horizon, arrivals, rainfall, temp, humidity):
    subset = df[(df.crop == crop) & (df.market == market)].sort_values("date")
    if subset.empty:
        subset = df[df.crop == crop].sort_values("date")
    latest = subset.iloc[-1]
    # The demo uses the latest observed price as the lag input.
    # Horizon is represented by the forecast month; this is a compact mini-project baseline.
    forecast_date = pd.Timestamp.today().normalize() + pd.Timedelta(days=horizon)
    return pd.DataFrame([{
        "crop": crop, "market": market, "month": int(forecast_date.month),
        "price_lag_1": float(latest["modal_price"]),
        "price_avg_7": float(subset.tail(7)["modal_price"].mean()),
        "arrivals": float(arrivals), "rainfall_mm": float(rainfall),
        "temperature_c": float(temp), "humidity": float(humidity)
    }]), forecast_date, float(latest["modal_price"])

st.title("🌾 AI-Based Crop Price Prediction")
st.caption("Mini project · XGBoost regression · SHAP explanations · Karnataka demo markets")

st.warning(
    "Dataset notice: this starter project includes SIMULATED demonstration records, "
    "not official mandi prices. Predictions and SHAP explanations are demonstrations only. "
    "Replace the CSV with verified AGMARKNET/data.gov.in records before academic evaluation."
)

df = load_data()
model, features, metrics = train_model(df)

with st.sidebar:
    st.header("Prediction inputs")
    crop = st.selectbox("Crop", sorted(df.crop.unique()))
    markets = sorted(df[df.crop == crop].market.unique())
    market = st.selectbox("Market", markets)
    horizon = st.selectbox("Forecast horizon", [7, 15, 30], index=0, format_func=lambda x: f"{x} days")
    st.divider()
    st.subheader("Latest-condition assumptions")
    arrivals = st.number_input("Expected arrivals (quintals)", min_value=0.0, value=100.0, step=10.0)
    rainfall = st.number_input("Rainfall (mm)", min_value=0.0, value=3.0, step=1.0)
    temp = st.number_input("Temperature (°C)", min_value=0.0, max_value=55.0, value=28.0, step=0.5)
    humidity = st.slider("Humidity (%)", 0, 100, 65)

st.subheader("Prediction")
row, forecast_date, current_price = make_features(
    df, crop, market, horizon, arrivals, rainfall, temp, humidity
)
predicted = max(0.0, float(model.predict(row[features])[0]))
change = ((predicted-current_price)/current_price*100) if current_price else 0.0

c1, c2, c3 = st.columns(3)
c1.metric("Latest demo modal price", f"₹{current_price:,.0f}/quintal")
c2.metric(f"Predicted price in {horizon} days", f"₹{predicted:,.0f}/quintal", f"{change:+.1f}%")
c3.metric("Forecast date", forecast_date.strftime("%d %b %Y"))
st.caption("The percentage compares the model estimate with the latest bundled demonstration price. It is not a guaranteed return.")

st.subheader("Why did the model predict this price?")
try:
    prep = model.named_steps["prep"]
    xgb = model.named_steps["xgb"]
    transformed = prep.transform(row[features])
    feature_names = prep.get_feature_names_out()
    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer(transformed)
    vals = np.array(shap_values.values).reshape(-1)
    base_value = float(np.array(shap_values.base_values).reshape(-1)[0])
    explanation = pd.DataFrame({"Feature": feature_names, "SHAP contribution (₹)": vals})
    explanation["Direction"] = np.where(explanation["SHAP contribution (₹)"] >= 0, "Pushes price up", "Pushes price down")
    explanation["Magnitude"] = explanation["SHAP contribution (₹)"].abs()
    explanation = explanation.sort_values("Magnitude", ascending=False).head(8)
    left, right = st.columns([1.2, 1])
    with left:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        colors = ["#218c52" if v >= 0 else "#cf5555" for v in explanation["SHAP contribution (₹)"][::-1]]
        ax.barh(explanation["Feature"][::-1], explanation["SHAP contribution (₹)"][::-1], color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Contribution to prediction (₹/quintal)")
        ax.set_title("Top SHAP contributions")
        st.pyplot(fig, clear_figure=True)
    with right:
        st.write("**Largest contributing factors**")
        for _, item in explanation.head(5).iterrows():
            direction = "increased" if item["SHAP contribution (₹)"] >= 0 else "reduced"
            st.write(f"- `{item['Feature']}` {direction} the model estimate by approximately ₹{abs(item['SHAP contribution (₹)']):,.1f}.")
        st.caption(f"Model baseline value: ₹{base_value:,.1f}/quintal. SHAP contributions sum to the model prediction (subject to rounding).")
except Exception as e:
    st.info(f"SHAP explanation could not be generated: {e}")

st.subheader("Historical demo price trend")
trend = df[(df.crop == crop) & (df.market == market)].sort_values("date").tail(90)
fig, ax = plt.subplots(figsize=(11, 3.5))
ax.plot(trend["date"], trend["modal_price"], label="Demo modal price")
ax.axhline(predicted, linestyle="--", label="Current model estimate")
ax.set_ylabel("₹ per quintal")
ax.legend()
ax.grid(alpha=0.2)
st.pyplot(fig, clear_figure=True)

with st.expander("Model evaluation (chronological holdout)"):
    st.write("The metrics below are calculated on the final 20% of the bundled demo records. They are not evidence of real-world forecasting accuracy.")
    st.json({k: round(float(v), 3) for k, v in metrics.items()})

with st.expander("Dataset preview"):
    st.dataframe(df.tail(20), use_container_width=True)

st.subheader("Decision-support note")
if change > 3:
    st.success("The model indicates an upward price direction. A farmer may compare this estimate with storage, transport, quality-loss and cash-flow costs before deciding to wait.")
elif change < -3:
    st.warning("The model indicates a downward price direction. A farmer may consider selling sooner, while checking local market conditions and transaction costs.")
else:
    st.info("The model indicates a relatively stable price. Continue monitoring verified market prices.")
st.caption("This is decision support, not financial or agricultural advice. The model uses assumed future conditions entered in the sidebar.")
