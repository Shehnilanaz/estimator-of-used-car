"""Used-Car Price Estimator — Streamlit app.

Loads used-cars.csv, trains a RandomForestRegressor at startup, and shows a
fair-price estimate with a low-high range. See TECHNICAL.md for the design.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Used-Car Price Estimator", page_icon="\U0001F697")

# --- Config -----------------------------------------------------------------
DATA_PATH = Path(__file__).parent / "used-cars.csv"

FEATURES = ["brand", "model", "year", "mileage_miles", "fuel_type", "transmission"]
CATEGORICAL = ["brand", "model", "fuel_type", "transmission"]

# The four transmission choices offered in the UI (FUNCTIONAL.md).
TRANSMISSIONS = ["Automatic", "Manual", "CVT", "Not specified"]

# Where our data ends — outside these, we show a "rough guide" flag.
YEAR_MIN_DATA, YEAR_MAX_DATA = 1998, 2024
MILEAGE_MAX_DATA = 300_000


# --- Data + model -----------------------------------------------------------
def group_transmission(value: str) -> str:
    """Collapse the 60 raw transmission values in the CSV into 4 clean groups."""
    v = str(value).strip().lower()
    if "cvt" in v or "variable" in v:
        return "CVT"
    if "auto" in v or "a/t" in v or "dual shift" in v or re.search(r"\bat\b", v):
        return "Automatic"
    if "manual" in v or "m/t" in v:
        return "Manual"
    return "Not specified"


@st.cache_resource(show_spinner="Training the model on 3,915 listings...")
def load_and_train():
    """Load the CSV, prepare features, and fit the model (once per app start)."""
    df = pd.read_csv(DATA_PATH)
    for col in ["year", "mileage_miles", "price_usd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=FEATURES + ["price_usd"])
    df["transmission"] = df["transmission"].map(group_transmission)

    X = pd.get_dummies(df[FEATURES], columns=CATEGORICAL)
    y = df["price_usd"]

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    models_by_brand = (
        df.groupby("brand")["model"].apply(lambda s: sorted(s.unique())).to_dict()
    )
    return df, model, X.columns, models_by_brand


def encode(car, train_columns):
    """Turn one car description into the model's numeric input."""
    row = pd.DataFrame([car])
    return pd.get_dummies(row, columns=CATEGORICAL).reindex(columns=train_columns, fill_value=0)


def predict_one(model, train_columns, car):
    return float(model.predict(encode(car, train_columns))[0])


def estimate_price(model, train_columns, car):
    """Return (estimate, low, high) rounded to the nearest $100."""
    row = encode(car, train_columns)

    point = float(model.predict(row)[0])
    # Spread of the individual trees' predictions -> low-high range.
    tree_preds = np.array([tree.predict(row)[0] for tree in model.estimators_])
    low, high = np.percentile(tree_preds, [10, 90])
    low, high = min(low, point), max(high, point)  # range always contains the estimate

    return (
        round(point / 100) * 100,
        round(low / 100) * 100,
        round(high / 100) * 100,
    )


def typical_car(df):
    """A plain average car from the data — the baseline factors compare against."""
    return {
        "brand": df["brand"].mode()[0],
        "model": df["model"].mode()[0],
        "year": int(df["year"].median()),
        "mileage_miles": int(df["mileage_miles"].median()),
        "fuel_type": df["fuel_type"].mode()[0],
        "transmission": df["transmission"].mode()[0],
    }


def describe_factor(field, value, typical_value, moved):
    """Turn one model effect into a plain-English line."""
    amount = round(abs(moved) / 100) * 100
    if moved > 0:
        tail = f"added value (about ${amount:,.0f})"
    else:
        tail = f"pulled it down (about ${amount:,.0f})"

    if field == "mileage_miles":
        desc = "Low mileage" if value < typical_value else "High mileage"
    elif field == "year":
        desc = "Newer model year" if value > typical_value else "Older model year"
    elif field == "fuel_type":
        desc = f"Fuel: {value}"
    elif field == "transmission":
        desc = f"Transmission: {value}"
    elif field == "brand":
        desc = f"Brand: {value}"
    else:  # model
        name = value if len(value) <= 40 else value[:37] + "..."
        desc = f"Model: {name}"
    return f"{desc} {tail}"


def top_factors(model, train_columns, car, typical, top_n=3):
    """The inputs that moved the estimate most vs. a typical car, biggest first."""
    base = predict_one(model, train_columns, car)
    effects = []
    for field in car:
        swapped = dict(car, **{field: typical[field]})
        moved = base - predict_one(model, train_columns, swapped)
        effects.append((abs(moved), moved, field))
    effects.sort(reverse=True)

    lines = []
    for magnitude, moved, field in effects[:top_n]:
        if magnitude < 50:  # moves under $50 aren't worth telling the user about
            continue
        lines.append(describe_factor(field, car[field], typical[field], moved))
    return lines


def similar_listings(df, car, estimate, n=3):
    """Closest real listings: same model first, then same family, then same brand."""
    is_same = (df["brand"] == car["brand"]) & (df["model"] == car["model"])
    family = car["model"].split()[0].lower()
    is_family = (df["brand"] == car["brand"]) & (
        df["model"].str.split().str[0].str.lower() == family
    )
    is_brand = df["brand"] == car["brand"]

    rows = []
    for pool in (df[is_same], df[is_family & ~is_same], df[is_brand & ~is_family], df[~is_brand]):
        pool = pool.assign(distance=(pool["price_usd"] - estimate).abs()).sort_values("distance")
        for record in pool.head(n - len(rows)).to_dict("records"):
            rows.append(record)
        if len(rows) >= n:
            break
    return rows


def format_listing(record):
    return {
        "Model": record["model"] if len(record["model"]) <= 44 else record["model"][:41] + "...",
        "Year": int(record["year"]),
        "Miles": f"{int(record['mileage_miles']):,}",
        "Price": f"${record['price_usd']:,.0f}",
    }


# --- Screen -----------------------------------------------------------------
st.title("\U0001F697 Used-Car Price Estimator")
st.caption("Fair-price estimate from 3,915 real used-car listings.")

if not DATA_PATH.exists():
    st.error(f"Dataset not found: `{DATA_PATH.name}` should sit next to `app.py`.")
    st.stop()

df, model, train_columns, models_by_brand = load_and_train()
brands = sorted(models_by_brand)

col1, col2 = st.columns(2)
# Most common fuel first, so the default lands on Gasoline, not Diesel.
fuel_types = list(df["fuel_type"].value_counts().index)

with col1:
    brand = st.selectbox(
        "Brand",
        brands,
        index=brands.index("Toyota") if "Toyota" in brands else 0,
    )
    # Default to this brand's most common model rather than the alphabet-first one.
    common_models = df.loc[df["brand"] == brand, "model"].value_counts()
    model_name = st.selectbox(
        "Model",
        models_by_brand[brand],
        index=models_by_brand[brand].index(common_models.index[0]),
    )
    fuel = st.selectbox("Fuel type", fuel_types)
with col2:
    transmission = st.selectbox("Transmission", TRANSMISSIONS)
    year = st.number_input("Year", min_value=1900, value=2018, step=1)
    mileage = st.number_input("Mileage (miles)", min_value=0, value=60_000, step=1_000)

car = {
    "brand": brand,
    "model": model_name,
    "year": year,
    "mileage_miles": mileage,
    "fuel_type": fuel,
    "transmission": transmission,
}
estimate, low, high = estimate_price(model, train_columns, car)

st.subheader("Estimated fair price")
st.markdown(f"### ${estimate:,.0f}")
st.write(f"Likely range: **${low:,.0f} – ${high:,.0f}**")

# Flags for inputs outside our data (FUNCTIONAL.md).
if year < YEAR_MIN_DATA or year > YEAR_MAX_DATA:
    st.warning("Our data doesn't cover this year — treat this estimate as a rough guide.")
if mileage > MILEAGE_MAX_DATA:
    st.warning("That mileage is beyond our data (up to 300,000 miles) — treat this estimate as a rough guide.")

# What moved this price (Step 5).
st.subheader("What moved this price")
factors = top_factors(model, train_columns, car, typical_car(df))
if factors:
    for line in factors:
        st.write(f"- {line}")
else:
    st.write("Nothing moves this price much — it's close to a typical car in our data.")

# Sanity check: the 3 most similar real listings.
st.subheader("3 most similar real listings")
similar = similar_listings(df, car, estimate)
st.table(pd.DataFrame([format_listing(r) for r in similar]))

st.caption(
    "Trained on all 3,915 listings each time the app starts · "
    "range = the spread of the model's decision trees · "
    "similar listings = closest real asking prices to this estimate"
)
