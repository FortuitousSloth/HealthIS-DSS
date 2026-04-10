import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import inject_css, train_model, PRIMARY, AF_COLOR, NO_AF_COLOR

st.set_page_config(page_title="EDA | AF DSS", page_icon="📊", layout="wide")
inject_css()
# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🫀 AF Risk DSS")
st.sidebar.markdown("---")
if st.sidebar.button("🏠 Home",              use_container_width=True): st.switch_page("app.py")
if st.sidebar.button("🔍 Risk Assessment",   use_container_width=True): st.switch_page("pages/1_Risk_Assessment.py")
if st.sidebar.button("📊 EDA",               use_container_width=True): st.switch_page("pages/2_EDA.py")
if st.sidebar.button("📈 Model Performance", use_container_width=True): st.switch_page("pages/3_Model_Performance.py")
if st.sidebar.button("🔬 What-If Analysis",  use_container_width=True): st.switch_page("pages/4_What_If.py")
st.sidebar.markdown("---")

model, scaler, X_train, X_test, y_train, y_test = train_model()

from prep_data import df_model
plot_df = df_model.copy()
plot_df["AF Status"] = plot_df["FIBR_PREDS"].map({0: "No AF", 1: "AF"})

coef_df = pd.DataFrame({
    "Feature": X_train.columns,
    "Coefficient": model.coef_[0],
}).assign(abs=lambda d: d["Coefficient"].abs()).sort_values("abs", ascending=False)

FRIENDLY = {
    "nr03":      "Prior paroxysmal AF",
    "nr04":      "Prior persistent AF",
    "nr11":      "Any arrhythmia history",
    "nr01":      "Prior atrial contractions",
    "nr02":      "Prior ventricular contractions",
    "endocr_01": "Diabetes",
    "endocr_02": "Obesity",
    "endocr_03": "Thyrotoxicosis",
    "SIM_GIPERT":"Symptomatic hypertension",
    "IBS_POST":  "Post-MI angina",
    "zab_leg_01":"Chronic lung disease",
    "zab_leg_02":"Obstructive lung disease",
    "np05":      "Bundle branch block",
    "np08":      "AV conduction issue",
}

BASE = dict(font=dict(family="Inter"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1E3A5F; margin-bottom:0.2rem;">📊 Exploratory Data Analysis</h1>', unsafe_allow_html=True)
st.write("Dataset: **1,700** post-MI patients | **35** predictors | AF incidence: **10%**")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Section 1: Demographics & target ─────────────────────────────────────────
st.markdown('<div class="section-title">Patient Demographics & Target Variable</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    counts = plot_df["FIBR_PREDS"].value_counts().reset_index()
    counts.columns = ["FIBR_PREDS", "Count"]
    counts["Label"] = counts["FIBR_PREDS"].map({0: "No AF  (90%)", 1: "AF  (10%)"})
    fig = px.bar(counts, x="Label", y="Count", color="Label",
                 color_discrete_map={"No AF  (90%)": NO_AF_COLOR, "AF  (10%)": AF_COLOR},
                 text="Count", title="AF Class Distribution")
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis_title="Patients", **BASE)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Heavy 9:1 class imbalance — the model uses `class_weight='balanced'` to compensate.")

with c2:
    fig = px.histogram(plot_df, x="AGE", color="AF Status", barmode="overlay",
                       nbins=22, opacity=0.78,
                       color_discrete_map={"No AF": NO_AF_COLOR, "AF": AF_COLOR},
                       title="Age Distribution by AF Status")
    fig.update_layout(xaxis_title="Age (years)", yaxis_title="Patients", **BASE)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("AF patients skew slightly older — consistent with clinical literature.")

with c3:
    sex_df = (plot_df.groupby("SEX")["FIBR_PREDS"].mean().reset_index()
              .assign(SEX=lambda d: d["SEX"].map({0: "Female", 1: "Male"}),
                      Rate=lambda d: (d["FIBR_PREDS"] * 100).round(1)))
    fig = px.bar(sex_df, x="SEX", y="Rate", color="SEX",
                 color_discrete_map={"Female": "#A78BFA", "Male": "#34D399"},
                 text="Rate", title="AF Rate by Sex")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_title="AF Rate (%)", yaxis_range=[0, 18], **BASE)
    st.plotly_chart(fig, use_container_width=True)

# ── Section 2: Predictors & vitals ───────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Predictors & Admission Vitals</div>', unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)

with c4:
    top12 = coef_df.head(12).copy()
    top12["Direction"] = top12["Coefficient"].apply(lambda x: "Increases Risk" if x > 0 else "Decreases Risk")
    top12["Feature"]   = top12["Feature"].map(lambda f: FRIENDLY.get(f, f))
    top12 = top12.sort_values("abs")
    fig = px.bar(top12, x="Coefficient", y="Feature", orientation="h", color="Direction",
                 color_discrete_map={"Increases Risk": AF_COLOR, "Decreases Risk": NO_AF_COLOR},
                 title="Top 12 Predictors (LR Coefficients)")
    fig.update_layout(yaxis_title="", xaxis_title="Coefficient",
                      legend=dict(orientation="h", y=-0.18), **BASE)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Larger magnitude = stronger influence on predicted AF risk.")

with c5:
    fig = px.box(plot_df, x="AF Status", y="S_AD_KBRIG", color="AF Status",
                 color_discrete_map={"No AF": NO_AF_COLOR, "AF": AF_COLOR},
                 points="outliers", title="Systolic BP at Admission")
    fig.update_layout(showlegend=False, yaxis_title="Systolic BP (mmHg)", **BASE)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    fig = px.box(plot_df, x="AF Status", y="D_AD_KBRIG", color="AF Status",
                 color_discrete_map={"No AF": NO_AF_COLOR, "AF": AF_COLOR},
                 points="outliers", title="Diastolic BP at Admission")
    fig.update_layout(showlegend=False, yaxis_title="Diastolic BP (mmHg)", **BASE)
    st.plotly_chart(fig, use_container_width=True)

# ── Section 3: AF rate by binary risk factors ─────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">AF Rate by Key Binary Risk Factors</div>', unsafe_allow_html=True)
st.caption("Percentage of patients who developed AF, split by whether each risk factor was present or absent.")

binary_cols = [c for c in FRIENDLY if c in df_model.columns]
rates = []
for col in binary_cols:
    for val in [0, 1]:
        subset = df_model[df_model[col] == val]
        if len(subset) > 10:
            rates.append({"Risk Factor": FRIENDLY[col], "Present": "Yes" if val == 1 else "No",
                          "AF Rate (%)": round(subset["FIBR_PREDS"].mean() * 100, 1), "N": len(subset)})

rates_df = pd.DataFrame(rates)
fig = px.bar(rates_df, x="Risk Factor", y="AF Rate (%)", color="Present", barmode="group",
             color_discrete_map={"Yes": AF_COLOR, "No": NO_AF_COLOR},
             hover_data=["N"], text="AF Rate (%)")
fig.update_traces(texttemplate="%{text}%", textposition="outside")
fig.update_layout(xaxis_tickangle=-28, yaxis_title="AF Rate (%)",
                  legend_title="Risk Factor Present", **BASE)
st.plotly_chart(fig, use_container_width=True)

# ── Section 4: Strip plot + summary ──────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Summary Statistics</div>', unsafe_allow_html=True)

c7, c8 = st.columns([3, 2])
with c7:
    fig = px.strip(plot_df, x="AF Status", y="AGE", color="AF Status",
                   color_discrete_map={"No AF": NO_AF_COLOR, "AF": AF_COLOR},
                   title="Age Distribution (Strip Plot) by AF Status")
    fig.update_traces(jitter=0.4, marker_size=3, opacity=0.5)
    fig.update_layout(showlegend=False, yaxis_title="Age (years)", **BASE)
    st.plotly_chart(fig, use_container_width=True)

with c8:
    st.markdown("<br>", unsafe_allow_html=True)
    summary = df_model.groupby("FIBR_PREDS")[["AGE","S_AD_KBRIG","D_AD_KBRIG"]].mean().round(1)
    summary.index = ["No AF (n=1,530)", "AF (n=170)"]
    summary.columns = ["Mean Age", "Mean Systolic BP", "Mean Diastolic BP"]
    st.dataframe(summary, use_container_width=True)

    total = len(df_model)
    af_n  = int(df_model["FIBR_PREDS"].sum())
    st.markdown(f"""
    <div class="info-box" style="margin-top:1rem;">
        <strong>Total:</strong> {total:,} patients |
        <strong>AF:</strong> {af_n} ({af_n/total:.1%}) |
        <strong>No AF:</strong> {total-af_n:,} ({(total-af_n)/total:.1%})
    </div>
    """, unsafe_allow_html=True)
