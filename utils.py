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

# ── Decision threshold ───────────────────────────────────────────────────────
# Lowered from 0.5 → 0.3 to maximise recall in this clinical AF detection task.
# At threshold 0.3 the model catches 57% of AF cases vs 49% at 0.5,
# at the cost of more false alarms — an acceptable trade-off for early detection.
THRESHOLD = 0.3


# ── Risk category ────────────────────────────────────────────────────────────
def risk_category(prob):
    """Classify AF probability into risk bands aligned with THRESHOLD=0.3."""
    if prob < 0.15:
        return "Low Risk", LOW_COLOR, "🟢"
    elif prob < THRESHOLD:
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
        background: linear-gradient(160deg, #ffffff 0%, #f0f4ff 100%);
        border-radius: 16px;
        padding: 1.6rem 1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(30,58,95,0.10);
        border-top: 4px solid #1E3A5F;
        margin-bottom: 1rem;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(30,58,95,0.16);
    }
    .stat-value { font-size: 2.2rem; font-weight: 700; color: #1E3A5F; line-height: 1.2; }
    .stat-label { font-size: 0.8rem; color: #6B7280; font-weight: 500; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── Risk cards ── */
    .risk-card {
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin: 0.8rem 0;
        border-left: 5px solid;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: box-shadow 0.18s ease;
    }
    .risk-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.10); }
    .risk-low  { background: linear-gradient(135deg,#D1FAE5 0%,#ECFDF5 100%); border-color:#10B981; }
    .risk-med  { background: linear-gradient(135deg,#FEF3C7 0%,#FFFBEB 100%); border-color:#F59E0B; }
    .risk-high { background: linear-gradient(135deg,#FEE2E2 0%,#FFF5F5 100%); border-color:#EF4444; }
    .risk-label { font-size:1.35rem; font-weight:700; margin-bottom:0.5rem; }
    .risk-low  .risk-label { color:#065F46; }
    .risk-med  .risk-label { color:#92400E; }
    .risk-high .risk-label { color:#991B1B; }
    .risk-rec { font-size:0.92rem; color:#374151; line-height:1.6; }

    /* ── Section titles ── */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E3A5F;
        padding: 0.5rem 0 0.5rem 0.8rem;
        border-left: 4px solid #1E3A5F;
        background: linear-gradient(90deg, rgba(30,58,95,0.05) 0%, transparent 100%);
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.2rem;
        letter-spacing: 0.01em;
    }

    /* ── Hero banner ── */
    .hero {
        background: linear-gradient(135deg, #0f2441 0%, #1E3A5F 45%, #2d6a9f 100%);
        border-radius: 18px;
        padding: 3rem 3rem;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30,58,95,0.25);
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -40%; left: -10%;
        width: 60%; height: 200%;
        background: rgba(255,255,255,0.04);
        transform: rotate(-15deg);
        border-radius: 50%;
    }
    .hero h1 { font-size:2.5rem; font-weight:700; margin:0 0 0.6rem 0; color:white !important; letter-spacing:-0.01em; }
    .hero p  { font-size:1.05rem; opacity:0.80; margin:0; font-weight:300; }

    /* ── Info / warning boxes ── */
    .info-box {
        background: linear-gradient(135deg,#EFF6FF 0%,#DBEAFE 100%);
        border-radius: 10px;
        padding: 1rem 1.4rem;
        border-left: 4px solid #3B82F6;
        margin: 0.8rem 0;
        font-size: 0.92rem;
        color: #1E40AF;
        line-height: 1.6;
        box-shadow: 0 1px 6px rgba(59,130,246,0.08);
    }
    .warn-box {
        background: linear-gradient(135deg,#FFFBEB 0%,#FEF3C7 100%);
        border-radius: 10px;
        padding: 1rem 1.4rem;
        border-left: 4px solid #F59E0B;
        margin: 0.8rem 0;
        font-size: 0.92rem;
        color: #92400E;
        line-height: 1.6;
        box-shadow: 0 1px 6px rgba(245,158,11,0.08);
    }

    /* ── Nav cards ── */
    .nav-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(30,58,95,0.08);
        border-bottom: 3px solid #1E3A5F;
        height: 100%;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(30,58,95,0.15);
    }
    .nav-card h3 { color:#1E3A5F; margin:0 0 0.5rem 0; font-size:1rem; font-weight:600; }
    .nav-card p  { color:#6B7280; font-size:0.85rem; margin:0; line-height:1.5; }

    /* ── Divider ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, #1E3A5F 0%, rgba(30,58,95,0.2) 60%, transparent 100%);
        border-radius: 2px;
        margin: 1.8rem 0;
    }

    /* ── Outcome badge ── */
    .outcome-badge {
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        margin-top: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .outcome-badge .ob-label { font-size:1.15rem; font-weight:700; }
    .outcome-badge .ob-sub   { font-size:0.8rem; color:#6B7280; margin-top:6px; }

    /* ── Streamlit widget tweaks ── */
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D5986 100%) !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8faff 0%, #f0f4ff 100%);
        border-right: 1px solid #e2e8f0;
    }
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
