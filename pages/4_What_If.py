import streamlit as st
import pandas as pd
from utils import inject_css, train_model, get_fill_values, risk_category, make_gauge, AF_COLOR, NO_AF_COLOR
from database.db import fetch_patient, patient_to_features, MODEL_COLUMNS

inject_css()

# ── Sidebar ────────────────────────────────────────────────────────────────

model, scaler, X_train, X_test, y_train, y_test = train_model()
fill_values = get_fill_values()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1E3A5F; margin-bottom:0.2rem;">🔬 What-If Analysis</h1>', unsafe_allow_html=True)
st.write("Adjust a patient's clinical parameters and watch the AF risk score update in real time.")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Sidebar: load a real patient ──────────────────────────────────────────────
st.sidebar.header("Base Patient")
st.sidebar.write("Start from population averages or load a real patient from the database.")
use_db = st.sidebar.checkbox("Load from database", value=False)

# Use a session-state key suffix so sliders reset when a new patient is loaded
if "wif_key" not in st.session_state:
    st.session_state["wif_key"] = 0
if "wif_base" not in st.session_state:
    st.session_state["wif_base"] = dict(fill_values)

if use_db:
    pid = st.sidebar.number_input("Patient ID", min_value=1, step=1, value=1)
    if st.sidebar.button("Load Patient", type="primary"):
        row = fetch_patient(int(pid))
        if row:
            feat_df = patient_to_features(row, fill_values)
            new_base = {col: float(feat_df[col].iloc[0]) for col in MODEL_COLUMNS}
            st.session_state["wif_base"] = new_base
            st.session_state["wif_key"] += 1   # force slider reset
            st.sidebar.success(f"Loaded patient {pid}")
        else:
            st.sidebar.error("Patient not found.")

if st.sidebar.button("Reset to averages"):
    st.session_state["wif_base"] = dict(fill_values)
    st.session_state["wif_key"] += 1

base    = st.session_state["wif_base"]
key_sfx = st.session_state["wif_key"]

# ── Controls + live gauge ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">Clinical Parameters</div>', unsafe_allow_html=True)
st.caption("Sliders default to population averages. Load a real patient from the sidebar to start from their values.")

ctrl_col, gauge_col = st.columns([3, 2])

with ctrl_col:
    r1, r2 = st.columns(2)

    with r1:
        st.markdown("**Demographics & Vitals**")
        age      = st.slider("Age (years)",          26, 92,  int(base.get("AGE", 62)),          key=f"age_{key_sfx}")
        sex      = st.selectbox("Sex",               [0, 1],  index=int(base.get("SEX", 1)),      key=f"sex_{key_sfx}",
                                format_func=lambda x: "Female" if x == 0 else "Male")
        sbp      = st.slider("Systolic BP (mmHg)",   60, 260, int(base.get("S_AD_KBRIG", 140)),  key=f"sbp_{key_sfx}")
        dbp      = st.slider("Diastolic BP (mmHg)",  40, 190, int(base.get("D_AD_KBRIG", 80)),   key=f"dbp_{key_sfx}")

        st.markdown("**Cardiac History**")
        inf_anam = st.slider("Prior MI count (0–3)",        0, 3, int(base.get("INF_ANAM", 0)),  key=f"inf_{key_sfx}")
        zsn_a    = st.slider("Heart failure history (0–4)", 0, 4, int(base.get("ZSN_A", 0)),     key=f"zsn_{key_sfx}")
        stenok   = st.slider("Angina severity (0–4)",       0, 4, int(base.get("STENOK_AN", 0)), key=f"sten_{key_sfx}")

    with r2:
        st.markdown("**Arrhythmia History**")
        nr11 = st.selectbox("Any arrhythmia in history",  [0,1], int(base.get("nr11", 0)), key=f"nr11_{key_sfx}", format_func=lambda x: "Yes" if x else "No")
        nr03 = st.selectbox("Prior paroxysmal AF",        [0,1], int(base.get("nr03", 0)), key=f"nr03_{key_sfx}", format_func=lambda x: "Yes" if x else "No")
        nr04 = st.selectbox("Prior persistent AF",        [0,1], int(base.get("nr04", 0)), key=f"nr04_{key_sfx}", format_func=lambda x: "Yes" if x else "No")
        nr01 = st.selectbox("Prior atrial contractions",  [0,1], int(base.get("nr01", 0)), key=f"nr01_{key_sfx}", format_func=lambda x: "Yes" if x else "No")

        st.markdown("**Comorbidities**")
        dm   = st.selectbox("Diabetes",                   [0,1], int(base.get("endocr_01", 0)), key=f"dm_{key_sfx}",  format_func=lambda x: "Yes" if x else "No")
        np05 = st.selectbox("Bundle branch block",        [0,1], int(base.get("np05", 0)),      key=f"np05_{key_sfx}", format_func=lambda x: "Yes" if x else "No")
        sim  = st.selectbox("Symptomatic hypertension",   [0,1], int(base.get("SIM_GIPERT", 0)),key=f"sim_{key_sfx}",  format_func=lambda x: "Yes" if x else "No")

# Build feature dict from sliders
current = dict(fill_values)  # start with all defaults
current.update({
    "AGE": age, "SEX": sex,
    "S_AD_KBRIG": sbp, "D_AD_KBRIG": dbp,
    "INF_ANAM": inf_anam, "ZSN_A": zsn_a, "STENOK_AN": stenok,
    "nr11": nr11, "nr03": nr03, "nr04": nr04, "nr01": nr01,
    "endocr_01": dm, "np05": np05, "SIM_GIPERT": sim,
})

feat_df     = pd.DataFrame([current], columns=MODEL_COLUMNS)
feat_scaled = scaler.transform(feat_df)
prob        = model.predict_proba(feat_scaled)[0, 1]
label, color, icon = risk_category(prob)

with gauge_col:
    st.plotly_chart(make_gauge(prob, height=300), use_container_width=True)

    css_cls = {"Low Risk": "risk-low", "Medium Risk": "risk-med", "High Risk": "risk-high"}[label]
    recs = {
        "Low Risk":    "Routine monitoring. Standard post-MI protocol.",
        "Medium Risk": "Increased rhythm surveillance. Clinical review within 24h.",
        "High Risk":   "Continuous monitoring. Early cardiology consultation.",
    }
    st.markdown(f"""
    <div class="risk-card {css_cls}">
        <div class="risk-label">{icon} {label}</div>
        <div class="risk-rec">{recs[label]}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Scenario comparison ───────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Scenario Comparison</div>', unsafe_allow_html=True)
st.caption("Save the current parameter configuration as a named scenario and compare multiple what-if cases.")

s_col1, s_col2 = st.columns([2, 1])
with s_col1:
    scenario_name = st.text_input("Scenario name", value=f"Scenario {len(st.session_state.get('scenarios', [])) + 1}")
with s_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    save_btn = st.button("💾 Save Scenario", type="primary")

if save_btn:
    if "scenarios" not in st.session_state:
        st.session_state["scenarios"] = []
    st.session_state["scenarios"].append({
        "Name":          scenario_name,
        "Age":           age,
        "Sex":           "Male" if sex else "Female",
        "Systolic BP":   sbp,
        "Prior AF":      "Yes" if (nr03 or nr04) else "No",
        "Arrhythmia Hx": "Yes" if nr11 else "No",
        "Diabetes":      "Yes" if dm else "No",
        "AF Probability":f"{prob:.1%}",
        "Risk Category": label,
    })
    st.success(f"Saved: {scenario_name}")

if st.session_state.get("scenarios"):
    scen_df = pd.DataFrame(st.session_state["scenarios"]).set_index("Name")
    st.dataframe(scen_df, use_container_width=True)

    import plotly.express as px
    chart_df = pd.DataFrame([{
        "Name": s["Name"],
        "Probability": float(s["AF Probability"].strip("%")) / 100,
        "Risk": s["Risk Category"],
    } for s in st.session_state["scenarios"]])
    color_map = {"Low Risk": "#10B981", "Medium Risk": "#F59E0B", "High Risk": "#EF4444"}
    fig = px.bar(chart_df, x="Name", y="Probability", color="Risk",
                 color_discrete_map=color_map,
                 text=chart_df["Probability"].map(lambda x: f"{x:.1%}"),
                 title="AF Probability Across Saved Scenarios")
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_tickformat=".0%", yaxis_range=[0, 1.1],
                      yaxis_title="AF Probability", xaxis_title="",
                      font=dict(family="Inter"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🗑️ Clear all scenarios"):
        st.session_state["scenarios"] = []
        st.rerun()
else:
    st.markdown("""
    <div class="info-box">
        Adjust parameters above and click <strong>Save Scenario</strong> to compare multiple configurations side by side.
    </div>
    """, unsafe_allow_html=True)
