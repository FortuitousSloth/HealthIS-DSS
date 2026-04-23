import streamlit as st
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
import pandas as pd
from utils import inject_css, train_model, get_fill_values, risk_category, make_gauge, THRESHOLD
from database.db import fetch_patient, fetch_all_patient_ids, patient_to_features

inject_css()
# ── Sidebar ────────────────────────────────────────────────────────────────

model, scaler, X_train, X_test, y_train, y_test = train_model()
fill_values = get_fill_values()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Patient Selection")
mode = st.sidebar.radio("Select by", ["Patient ID", "Browse list"])

if mode == "Patient ID":
    patient_id = st.sidebar.number_input("Enter Patient ID", min_value=1, step=1, value=1)
else:
    with st.spinner("Loading patient list…"):
        all_ids = fetch_all_patient_ids()
    patient_id = st.sidebar.selectbox("Choose a patient", all_ids)

assess = st.sidebar.button("Assess Risk", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Risk thresholds**
- 🟢 < 15% → Low Risk
- 🟡 15–{int(THRESHOLD*100)}% → Medium Risk
- 🔴 ≥ {int(THRESHOLD*100)}% → High Risk
""")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1E3A5F; margin-bottom:0.2rem;">🔍 Patient Risk Assessment</h1>', unsafe_allow_html=True)
st.write("Look up a patient from the database and get their predicted AF risk with a clinical recommendation.")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if not assess:
    st.markdown("""
    <div class="info-box">
        Pick a patient from the sidebar and click <strong>Assess Risk</strong> to get started.
    </div>
    """, unsafe_allow_html=True)
else:
    with st.spinner("Fetching from database…"):
        row = fetch_patient(int(patient_id))

    if row is None:
        st.error(f"Patient ID {patient_id} not found in the database.")
    else:
        from database.db import MODEL_COLUMNS
        features_df    = patient_to_features(row, fill_values)
        features_scaled = scaler.transform(features_df)
        prob            = model.predict_proba(features_scaled)[0, 1]
        label, color, icon = risk_category(prob)
        actual          = row.get("fibr_preds")

        # ── Top row: gauge | risk card | outcome ─────────────────────────────
        g_col, r_col, o_col = st.columns([2, 2, 1])

        with g_col:
            st.plotly_chart(make_gauge(prob, height=290), use_container_width=True)

        with r_col:
            css_cls = {"Low Risk": "risk-low", "Medium Risk": "risk-med", "High Risk": "risk-high"}[label]
            recs = {
                "Low Risk":    "Routine cardiac monitoring. Standard post-MI management protocol.",
                "Medium Risk": "Increased rhythm surveillance. Clinical review recommended within 24 hours.",
                "High Risk":   "Continuous cardiac monitoring. Early cardiology consultation advised. Consider electrolyte management.",
            }
            st.markdown(f"""
            <div class="risk-card {css_cls}">
                <div class="risk-label">{icon} {label}</div>
                <div class="risk-rec">
                    <strong>Clinical Recommendation:</strong><br>{recs[label]}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with o_col:
            if actual is not None:
                af_occurred = int(actual) == 1
                correct = (af_occurred and prob >= THRESHOLD) or (not af_occurred and prob < THRESHOLD)
                bg   = "#FEE2E2" if af_occurred else "#D1FAE5"
                clr  = "#991B1B" if af_occurred else "#065F46"
                olbl = "AF Occurred" if af_occurred else "No AF"
                st.markdown(f"""
                <div class="outcome-badge" style="background:{bg};">
                    <div class="ob-label" style="color:{clr};">{olbl}</div>
                    <div class="ob-sub">{"✅ Correct" if correct else "❌ Incorrect"} prediction</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Patient ID banner ─────────────────────────────────────────────────
        age = row.get("AGE") or features_df["AGE"].iloc[0]
        sex = "Male" if (row.get("SEX") or features_df["SEX"].iloc[0]) == 1 else "Female"
        st.markdown(f"""
        <div class="info-box" style="margin-top:1rem;">
            📋 <strong>Patient {int(patient_id)}</strong> — Age: {int(age) if age else 'N/A'} | Sex: {sex} |
            AF Probability: <strong>{prob:.1%}</strong> | Risk: <strong>{label}</strong>
        </div>
        """, unsafe_allow_html=True)

        # ── Patient record tabs ───────────────────────────────────────────────
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Patient Clinical Record</div>', unsafe_allow_html=True)

        display = features_df.T.copy()
        display.columns = ["Value"]
        display.index.name = "Feature"

        groups = {
            "👤 Demographics":         ["AGE", "SEX"],
            "🫀 Cardiovascular History": ["INF_ANAM","STENOK_AN","FK_STENOK","IBS_POST","IBS_NASL","GB","SIM_GIPERT","DLIT_AG","ZSN_A"],
            "⚡ Arrhythmia History":    ["nr11","nr01","nr02","nr03","nr04","nr07","nr08"],
            "🔌 Conduction History":    ["np01","np04","np05","np07","np08","np09","np10"],
            "💉 Other History":         ["endocr_01","endocr_02","endocr_03","zab_leg_01","zab_leg_02","zab_leg_03","zab_leg_04","zab_leg_06"],
            "🩺 Admission Vitals":       ["S_AD_KBRIG","D_AD_KBRIG"],
        }

        tabs = st.tabs(list(groups.keys()))
        for tab, (_, cols) in zip(tabs, groups.items()):
            with tab:
                grp_df = display[display.index.isin(cols)].copy()
                st.dataframe(grp_df, use_container_width=True, height=250)
