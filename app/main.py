import json
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

MODELS = Path(__file__).resolve().parent.parent / "models"
STATIC = Path(__file__).resolve().parent / "static"
model = xgb.XGBClassifier()
model.load_model(str(MODELS / "xgb_tuned.json"))
scaler = joblib.load(MODELS / "scaler.pkl")
feature_columns = joblib.load(MODELS / "feature_columns.pkl")
numeric_features = joblib.load(MODELS / "numeric_features.pkl")
threshold = float(joblib.load(MODELS / "threshold.pkl"))
with open(MODELS / "categories.json") as f:
    categories = json.load(f)

# In this dataset the scheduled days are fixed for each shipping mode
SCHEDULED_DAYS = {"First Class": 1, "Same Day": 0, "Second Class": 2, "Standard Class": 4}


def norm(s):
    return " ".join(str(s).split()).lower()


lookup = {col: {norm(v): v for v in vals} for col, vals in categories.items()}


def clean(col, value):
    v = lookup[col].get(norm(value))
    if v is None:
        raise HTTPException(status_code=422,
                            detail=f"Invalid {col}: '{value}'. Allowed: {categories[col]}")
    return v


app = FastAPI(title="DelayGuard - Late Delivery Risk Predictor",
              description="Predicts at order time whether an order is at risk of late delivery.")

app.mount("/assets", StaticFiles(directory=STATIC), name="assets")

class Order(BaseModel):
    order_date: str = "2017-09-21 09:49:00"
    shipping_mode: str = "Standard Class"
    payment_type: str = "DEBIT"
    category_id: int = 29
    department_id: int = 5
    department_name: str = "Fan Shop"
    market: str = "LATAM"
    order_region: str = "Central America"
    customer_country: str = "EE. UU."
    customer_segment: str = "Consumer"
    latitude: float = 18.0
    longitude: float = -66.0
    sales: float = 200.0
    sales_per_customer: float = 180.0
    order_item_product_price: float = 65.0
    order_item_discount: float = 10.0
    order_item_discount_rate: float = 0.1
    order_item_profit_ratio: float = 0.25
    benefit_per_order: float = 30.0


CATEGORICAL = ['Type', 'Customer Country', 'Customer Segment', 'Department Name',
               'Market', 'Order Region', 'Shipping Mode']


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/check")
def check():
    return FileResponse(STATIC / "check.html")


@app.get("/how-it-works")
def how_it_works():
    return FileResponse(STATIC / "how-it-works.html")


@app.get("/dataset")
def dataset():
    return FileResponse(STATIC / "dataset.html")


@app.get("/results")
def results():
    return FileResponse(STATIC / "results.html")


@app.get("/about")
def about():
    return FileResponse(STATIC / "about.html")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/options")
def options():
    return categories


@app.post("/predict")
def predict(o: Order):
    try:
        d = pd.to_datetime(o.order_date)
    except Exception:
        raise HTTPException(status_code=422,
                            detail="order_date must look like 2017-09-21 09:49:00")

    mode = clean('Shipping Mode', o.shipping_mode)

    row = pd.DataFrame([{
        'Type': clean('Type', o.payment_type),
        'Days for shipment (scheduled)': SCHEDULED_DAYS[mode],
        'Benefit per order': o.benefit_per_order,
        'Sales per customer': o.sales_per_customer,
        'Category Id': o.category_id,
        'Department Id': o.department_id,
        'Latitude': o.latitude,
        'Longitude': o.longitude,
        'Order Item Discount': o.order_item_discount,
        'Order Item Discount Rate': o.order_item_discount_rate,
        'Order Item Product Price': o.order_item_product_price,
        'Order Item Profit Ratio': o.order_item_profit_ratio,
        'Sales': o.sales,
        'order_month': d.month,
        'order_weekday': d.dayofweek,
        'order_hour': d.hour,
        'Customer Country': clean('Customer Country', o.customer_country),
        'Customer Segment': clean('Customer Segment', o.customer_segment),
        'Department Name': clean('Department Name', o.department_name),
        'Market': clean('Market', o.market),
        'Order Region': clean('Order Region', o.order_region),
        'Shipping Mode': mode,
    }])

    row = pd.get_dummies(row, columns=CATEGORICAL, drop_first=False)
    row = row.reindex(columns=feature_columns, fill_value=0).astype(float)
    row[numeric_features] = scaler.transform(row[numeric_features])

    p = float(model.predict_proba(row)[0, 1])
    high = p >= threshold

    contribs = model.get_booster().predict(xgb.DMatrix(row), pred_contribs=True)[0][:-1]
    top = sorted(zip(feature_columns, contribs), key=lambda x: abs(x[1]), reverse=True)[:3]
    reasons = [{"feature": f,
                "effect": "increases late risk" if v > 0 else "decreases late risk",
                "shap_value": round(float(v), 3)} for f, v in top]

    return {
        "late_probability": round(p, 4),
        "decision_threshold": round(threshold, 3),
        "prediction": "HIGH RISK of late delivery" if high else "LOW RISK",
        "suggested_action": "Prioritise this order or upgrade shipping" if high else "No action needed",
        "top_reasons": reasons,
        "note": "Uses only information available at order time. Coordinates, product category and profit fields use typical default values, so reasons based on them are indicative only.",
    }