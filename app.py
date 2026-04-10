import streamlit as st
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from prep_data import X_train, X_test, y_train, y_test
from database.db import fetch_patient, fetch_all_patient_ids, patient_to_features, MODEL_COLUMNS

# -----------------------------
# TRAIN MODEL (on historical data from prep_data.py)
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
model = LogisticRegression(max_iter=5000, class_weight="balanced")
model.fit(X_train_scaled, y_train)

# Precompute fill values (median/mode per column) from training data
# Mirrors the imputation logic in prep_data.py
fill_values = {}
for col in MODEL_COLUMNS:
    if col not in X_train.columns:
        fill_values[col] = 0
        continue
    unique_count = X_train[col].dropna().nunique()
    if unique_count <= 5:
        mode = X_train[col].mode(dropna=True)
        fill_values[col] = float(mode.iloc[0]) if not mode.empty else 0
    else:
        fill_values[col] = float(X_train[col].median())


# -----------------------------
# RISK CATEGORY FUNCTION
# -----------------------------
def risk_category(prob):
    if prob < 0.2:
        return "Low Risk"
    elif prob < 0.5:
        return "Medium Risk"
    else:
        return "High Risk"


# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("Atrial Fibrillation Risk DSS")
st.subheader("Post-MI In-Hospital AF Risk Assessment")

st.write(
    "This prototype estimates the risk of atrial fibrillation in hospitalized "
    "myocardial infarction patients using admission and history variables."
)

# --- Patient selection ---
st.sidebar.header("Patient Selection")
input_mode = st.sidebar.radio("Select patient by", ["Patient ID", "Browse list"])

patient_id = None

if input_mode == "Patient ID":
    patient_id = st.sidebar.number_input("Enter Patient ID", min_value=1, step=1, value=1)
else:
    with st.spinner("Loading patient list..."):
        all_ids = fetch_all_patient_ids()
    patient_id = st.sidebar.selectbox("Choose a patient", all_ids)

# --- Risk assessment ---
if st.sidebar.button("Assess Risk"):
    with st.spinner("Fetching patient record from database..."):
        row = fetch_patient(int(patient_id))

    if row is None:
        st.error(f"Patient ID {patient_id} not found in the database.")
    else:
        features_df = patient_to_features(row, fill_values)
        features_scaled = scaler.transform(features_df)

        prob = model.predict_proba(features_scaled)[0, 1]
        risk = risk_category(prob)
        actual = row.get("fibr_preds")

        # --- Results ---
        col1, col2 = st.columns(2)
        col1.metric("AF Probability", f"{prob:.1%}")
        col2.metric("Risk Category", risk)

        if risk == "Low Risk":
            st.success("**Recommendation:** Routine monitoring.")
        elif risk == "Medium Risk":
            st.warning("**Recommendation:** Increased rhythm surveillance and clinical review.")
        else:
            st.error("**Recommendation:** Close cardiac monitoring and consider early cardiology consultation.")

        if actual is not None:
            st.info(f"**Actual outcome (FIBR_PREDS):** {'AF occurred' if int(actual) == 1 else 'No AF'}")

        st.write("### Patient Record")
        display_df = features_df.T.copy()
        display_df.columns = ["Value"]
        st.dataframe(display_df)
