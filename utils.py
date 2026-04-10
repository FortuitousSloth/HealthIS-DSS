"""Shared utilities — model training, CSS, colors, and chart helpers."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# ── Color palette ────────────────────────────────────────────────────────────
PRIMARY     = "#1E3A5F"
LOW_COLOR   = "#10B981"
MED_COLOR   = "#F59E0B"
HIGH_COLOR  = "#EF4444"
AF_COLOR    = "#E8604C"
NO_AF_COLOR = "#4C9BE8"


# ── Risk category ────────────────────────────────────────────────────────────
def risk_category(prob):
    if prob < 0.2:
        return "Low Risk", LOW_COLOR, "🟢"
    elif prob < 0.5:
        return "Medium Risk", MED_COLOR, "🟡"
    else:
        return "High Risk", HIGH_COLOR, "🔴"


# ── Cached model training ────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Training model on historical data…")
def train_model():
    from prep_data import X_train, X_test, y_train, y_test
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression(max_iter=5000, class_weight="balanced", C=0.05)
    model.fit(X_train_scaled, y_train)
    return model, scaler, X_train, X_test, y_train, y_test


# ── Fill values (median/mode from training data) ─────────────────────────────
@st.cache_resource
def get_fill_values():
    from database.db import MODEL_COLUMNS
    _, _, X_train, _, _, _ = train_model()
    fill = {}
    for col in MODEL_COLUMNS:
        if col not in X_train.columns:
            fill[col] = 0.0
            continue
        n_unique = X_train[col].dropna().nunique()
        if n_unique <= 5:
            mode = X_train[col].mode(dropna=True)
            fill[col] = float(mode.iloc[0]) if not mode.empty else 0.0
        else:
            fill[col] = float(X_train[col].median())
    return fill


# ── Global CSS ───────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }

    /* ── Stat cards ── */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.4rem 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        border-top: 4px solid #1E3A5F;
        margin-bottom: 1rem;
    }
    .stat-value { font-size: 2.1rem; font-weight: 700; color: #1E3A5F; line-height: 1.2; }
    .stat-label { font-size: 0.82rem; color: #6B7280; font-weight: 500; margin-top: 4px; }

    /* ── Risk cards ── */
    .risk-card {
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin: 0.8rem 0;
        border-left: 5px solid;
    }
    .risk-low  { background:#D1FAE5; border-color:#10B981; }
    .risk-med  { background:#FEF3C7; border-color:#F59E0B; }
    .risk-high { background:#FEE2E2; border-color:#EF4444; }
    .risk-label { font-size:1.35rem; font-weight:700; margin-bottom:0.5rem; }
    .risk-low  .risk-label { color:#065F46; }
    .risk-med  .risk-label { color:#92400E; }
    .risk-high .risk-label { color:#991B1B; }
    .risk-rec { font-size:0.92rem; color:#374151; line-height:1.5; }

    /* ── Section titles ── */
    .section-title {
        font-size:1.2rem; font-weight:600; color:#1E3A5F;
        padding-bottom:0.45rem;
        border-bottom:2px solid #E5E7EB;
        margin-bottom:1.2rem;
    }

    /* ── Hero banner ── */
    .hero {
        background: linear-gradient(135deg,#1E3A5F 0%,#2D5986 100%);
        border-radius:16px; padding:2.8rem 3rem;
        color:white; margin-bottom:2rem; text-align:center;
    }
    .hero h1 { font-size:2.4rem; font-weight:700; margin:0 0 0.5rem 0; color:white !important; }
    .hero p  { font-size:1.05rem; opacity:0.85; margin:0; }

    /* ── Info / warning boxes ── */
    .info-box {
        background:#EFF6FF; border-radius:10px;
        padding:1rem 1.4rem; border-left:4px solid #3B82F6;
        margin:0.8rem 0; font-size:0.92rem; color:#1E40AF; line-height:1.5;
    }
    .warn-box {
        background:#FFFBEB; border-radius:10px;
        padding:1rem 1.4rem; border-left:4px solid #F59E0B;
        margin:0.8rem 0; font-size:0.92rem; color:#92400E; line-height:1.5;
    }

    /* ── Nav cards ── */
    .nav-card {
        background:white; border-radius:12px; padding:1.4rem;
        box-shadow:0 2px 10px rgba(0,0,0,0.07);
        border-bottom:3px solid #1E3A5F; height:100%;
    }
    .nav-card h3 { color:#1E3A5F; margin:0 0 0.5rem 0; font-size:1rem; }
    .nav-card p  { color:#6B7280; font-size:0.85rem; margin:0; line-height:1.5; }

    /* ── Divider ── */
    .divider {
        height:2px;
        background:linear-gradient(90deg,#1E3A5F 0%,transparent 100%);
        border-radius:2px; margin:1.6rem 0;
    }

    /* ── Outcome badge ── */
    .outcome-badge {
        border-radius:10px; padding:1rem;
        text-align:center; margin-top:0.5rem;
    }
    .outcome-badge .ob-label { font-size:1.15rem; font-weight:700; }
    .outcome-badge .ob-sub   { font-size:0.8rem; color:#6B7280; margin-top:6px; }
    </style>
    """, unsafe_allow_html=True)


# ── Gauge chart ──────────────────────────────────────────────────────────────
def make_gauge(prob, height=280):
    _, color, _ = risk_category(prob)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 48, "color": color, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickfont": {"size": 11}},
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  20], "color": "#D1FAE5"},
                {"range": [20, 50], "color": "#FEF3C7"},
                {"range": [50,100], "color": "#FEE2E2"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": prob * 100,
            },
        },
        title={"text": "AF Risk Probability", "font": {"size": 16, "color": PRIMARY, "family": "Inter"}},
    ))
    fig.update_layout(
        height=height,
        margin=dict(t=80, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    return fig
