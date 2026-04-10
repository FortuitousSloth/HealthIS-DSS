import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from prep_data import df_model, X_train, y_train

st.set_page_config(page_title="EDA – AF Risk DSS", layout="wide")
st.title("Exploratory Data Analysis")
st.write("Dataset: 1,700 post-MI patients | Target: In-hospital atrial fibrillation (FIBR_PREDS)")

# ── Precompute feature importances ──────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
model = LogisticRegression(max_iter=5000, class_weight="balanced")
model.fit(X_scaled, y_train)

importance_df = pd.DataFrame({
    "Feature": X_train.columns,
    "Coefficient": model.coef_[0]
}).sort_values("Coefficient", key=abs, ascending=False)

# ── Friendly labels for binary features ─────────────────────────────────────
BINARY_LABELS = {
    "nr03": "Prior paroxysmal AF",
    "nr04": "Prior persistent AF",
    "nr11": "Any arrhythmia history",
    "nr01": "Prior atrial contractions",
    "nr02": "Prior ventricular contractions",
    "endocr_01": "Diabetes",
    "endocr_02": "Obesity",
    "SIM_GIPERT": "Symptomatic hypertension",
    "IBS_POST": "Post-MI angina",
    "zab_leg_01": "Chronic lung disease",
}

# ════════════════════════════════════════════════════════════════════════════
# ROW 1 — Class distribution + Age distribution
# ════════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("AF Class Distribution")
    counts = df_model["FIBR_PREDS"].value_counts().reset_index()
    counts.columns = ["AF Occurred", "Count"]
    counts["AF Occurred"] = counts["AF Occurred"].map({0: "No AF (90%)", 1: "AF (10%)"})
    fig = px.bar(
        counts, x="AF Occurred", y="Count",
        color="AF Occurred",
        color_discrete_map={"No AF (90%)": "#4C9BE8", "AF (10%)": "#E8604C"},
        text="Count"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis_title="Number of Patients")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The dataset is heavily imbalanced — only 10% of patients experienced AF. "
               "This is why the model uses class weighting.")

with col2:
    st.subheader("Age Distribution by AF Status")
    plot_df = df_model.copy()
    plot_df["AF Status"] = plot_df["FIBR_PREDS"].map({0: "No AF", 1: "AF"})
    fig = px.histogram(
        plot_df, x="AGE", color="AF Status", barmode="overlay",
        nbins=20, opacity=0.75,
        color_discrete_map={"No AF": "#4C9BE8", "AF": "#E8604C"}
    )
    fig.update_layout(xaxis_title="Age", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("AF patients tend to be slightly older, consistent with clinical literature.")

# ════════════════════════════════════════════════════════════════════════════
# ROW 2 — AF rate by sex + Top feature importances
# ════════════════════════════════════════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.subheader("AF Rate by Sex")
    sex_df = df_model.groupby("SEX")["FIBR_PREDS"].mean().reset_index()
    sex_df["SEX"] = sex_df["SEX"].map({0: "Female", 1: "Male"})
    sex_df["AF Rate (%)"] = (sex_df["FIBR_PREDS"] * 100).round(1)
    fig = px.bar(
        sex_df, x="SEX", y="AF Rate (%)",
        color="SEX",
        color_discrete_map={"Female": "#A78BFA", "Male": "#34D399"},
        text="AF Rate (%)"
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_title="AF Rate (%)", yaxis_range=[0, 20])
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Top 10 Predictors (Model Coefficients)")
    top10 = importance_df.head(10).copy()
    top10["Direction"] = top10["Coefficient"].apply(lambda x: "Increases Risk" if x > 0 else "Decreases Risk")
    top10["abs"] = top10["Coefficient"].abs()
    top10 = top10.sort_values("abs")
    fig = px.bar(
        top10, x="Coefficient", y="Feature", orientation="h",
        color="Direction",
        color_discrete_map={"Increases Risk": "#E8604C", "Decreases Risk": "#4C9BE8"}
    )
    fig.update_layout(yaxis_title="", xaxis_title="Logistic Regression Coefficient")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Coefficients from the balanced logistic regression. "
               "Larger magnitude = stronger influence on AF prediction.")

# ════════════════════════════════════════════════════════════════════════════
# ROW 3 — Blood pressure boxplots
# ════════════════════════════════════════════════════════════════════════════
st.subheader("Admission Blood Pressure by AF Status")
col5, col6 = st.columns(2)

plot_df = df_model.copy()
plot_df["AF Status"] = plot_df["FIBR_PREDS"].map({0: "No AF", 1: "AF"})

with col5:
    fig = px.box(
        plot_df, x="AF Status", y="S_AD_KBRIG",
        color="AF Status",
        color_discrete_map={"No AF": "#4C9BE8", "AF": "#E8604C"},
        points="outliers"
    )
    fig.update_layout(showlegend=False, yaxis_title="Systolic BP (mmHg)",
                      title="Systolic BP")
    st.plotly_chart(fig, use_container_width=True)

with col6:
    fig = px.box(
        plot_df, x="AF Status", y="D_AD_KBRIG",
        color="AF Status",
        color_discrete_map={"No AF": "#4C9BE8", "AF": "#E8604C"},
        points="outliers"
    )
    fig.update_layout(showlegend=False, yaxis_title="Diastolic BP (mmHg)",
                      title="Diastolic BP")
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ROW 4 — AF rate by binary risk factors
# ════════════════════════════════════════════════════════════════════════════
st.subheader("AF Rate by Key Binary Risk Factors")
st.caption("Percentage of patients who developed AF, split by whether each risk factor was present (1) or absent (0).")

binary_cols = [c for c in BINARY_LABELS if c in df_model.columns]
rates = []
for col in binary_cols:
    for val in [0, 1]:
        subset = df_model[df_model[col] == val]
        if len(subset) > 0:
            rates.append({
                "Risk Factor": BINARY_LABELS[col],
                "Present": "Yes" if val == 1 else "No",
                "AF Rate (%)": round(subset["FIBR_PREDS"].mean() * 100, 1),
                "N": len(subset)
            })

rates_df = pd.DataFrame(rates)
fig = px.bar(
    rates_df, x="Risk Factor", y="AF Rate (%)",
    color="Present", barmode="group",
    color_discrete_map={"Yes": "#E8604C", "No": "#4C9BE8"},
    hover_data=["N"]
)
fig.update_layout(
    xaxis_tickangle=-30,
    yaxis_title="AF Rate (%)",
    legend_title="Risk Factor Present"
)
st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ROW 5 — Summary stats table
# ════════════════════════════════════════════════════════════════════════════
st.subheader("Summary Statistics")
summary = df_model.groupby("FIBR_PREDS")[["AGE", "S_AD_KBRIG", "D_AD_KBRIG"]].mean().round(1)
summary.index = ["No AF", "AF"]
summary.columns = ["Mean Age", "Mean Systolic BP", "Mean Diastolic BP"]
st.dataframe(summary, use_container_width=True)
