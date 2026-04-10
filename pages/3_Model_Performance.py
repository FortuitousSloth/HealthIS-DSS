import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    precision_recall_curve, accuracy_score,
    precision_score, recall_score, f1_score,
)
from utils import inject_css, train_model, PRIMARY, AF_COLOR, NO_AF_COLOR

st.set_page_config(page_title="Model Performance | AF DSS", page_icon="📈", layout="wide")
inject_css()
# ── Sidebar navigation ─────────────────────────────────────────────────────
st.sidebar.markdown("## 🫀 AF Risk DSS")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py",                       label="🏠 Home")
st.sidebar.page_link("pages/1_Risk_Assessment.py",   label="🔍 Risk Assessment")
st.sidebar.page_link("pages/2_EDA.py",               label="📊 EDA")
st.sidebar.page_link("pages/3_Model_Performance.py", label="📈 Model Performance")
st.sidebar.page_link("pages/4_What_If.py",           label="🔬 What-If Analysis")
st.sidebar.markdown("---")

model, scaler, X_train, X_test, y_train, y_test = train_model()
X_train_scaled = scaler.transform(X_train)
X_test_scaled  = scaler.transform(X_test)
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred, zero_division=0)
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

BASE = dict(font=dict(family="Inter"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 style="color:#1E3A5F; margin-bottom:0.2rem;">📈 Model Performance</h1>', unsafe_allow_html=True)
st.write("Evaluation of the **balanced logistic regression** on the held-out test set (20% of 1,700 patients).")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Key metric cards ──────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
for col, label, val in zip(
    [m1, m2, m3, m4, m5],
    ["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"],
    [f"{acc:.1%}", f"{prec:.1%}", f"{rec:.1%}", f"{f1:.1%}", f"{roc_auc:.3f}"],
):
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{val}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="warn-box">
    ⚠️ <strong>Recall is prioritised over precision</strong> in this clinical setting — missing an AF case (false negative)
    is more costly than a false alarm. The balanced model achieves recall ≈ 49% vs. near-zero for the baseline.
</div>
""", unsafe_allow_html=True)

# ── Confusion matrix + ROC ────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Confusion Matrix & ROC Curve</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fig = px.imshow(
        cm,
        labels=dict(x="Predicted", y="Actual", color="Count"),
        x=["No AF", "AF"],
        y=["No AF", "AF"],
        color_continuous_scale=[[0, "#EFF6FF"], [1, PRIMARY]],
        text_auto=True,
        title="Confusion Matrix",
    )
    fig.update_traces(textfont_size=22)
    fig.update_layout(height=340, margin=dict(t=50,b=20,l=20,r=20),
                      coloraxis_showscale=False, **BASE)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
    <div class="info-box">
        Of <strong>{len(y_test)}</strong> test patients — <strong>{tp}</strong> AF cases correctly flagged
        (recall {rec:.1%}), <strong>{fn}</strong> missed, <strong>{fp}</strong> false alarms,
        <strong>{tn}</strong> true negatives.
    </div>
    """, unsafe_allow_html=True)

with c2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", fill="tozeroy",
                             fillcolor="rgba(30,58,95,0.1)",
                             name=f"Balanced LR (AUC = {roc_auc:.3f})",
                             line=dict(color=PRIMARY, width=3)))
    fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                             name="Random classifier",
                             line=dict(dash="dash", color="#9CA3AF", width=2)))
    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
        height=340, margin=dict(t=50,b=40,l=40,r=20),
        legend=dict(x=0.38, y=0.08), **BASE,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── PR curve + Feature importance ────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Precision-Recall Curve & Feature Importances</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    prec_curve, rec_curve, _ = precision_recall_curve(y_test, y_prob)
    pr_auc   = auc(rec_curve, prec_curve)
    baseline = float(y_test.mean())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rec_curve, y=prec_curve, mode="lines",
                             name=f"Balanced LR (AUC = {pr_auc:.3f})",
                             line=dict(color=AF_COLOR, width=3),
                             fill="tozeroy", fillcolor="rgba(232,96,76,0.08)"))
    fig.add_hline(y=baseline, line_dash="dash", line_color="#9CA3AF",
                  annotation_text=f"No-skill baseline ({baseline:.1%})",
                  annotation_position="bottom right")
    fig.update_layout(
        title="Precision-Recall Curve",
        xaxis_title="Recall", yaxis_title="Precision",
        height=340, margin=dict(t=50,b=40,l=40,r=20),
        legend=dict(x=0.3, y=0.92), **BASE,
    )
    st.plotly_chart(fig, use_container_width=True)

with c4:
    FRIENDLY = {
        "nr03":"Prior paroxysmal AF","nr04":"Prior persistent AF",
        "nr11":"Arrhythmia history","AGE":"Age","np05":"Bundle branch block",
        "STENOK_AN":"Angina history","np08":"AV conduction","ZSN_A":"Heart failure hx",
        "S_AD_KBRIG":"Systolic BP","endocr_01":"Diabetes",
    }
    top15 = pd.DataFrame({"Feature": X_train.columns, "Coefficient": model.coef_[0]})
    top15["abs"] = top15["Coefficient"].abs()
    top15 = top15.sort_values("abs", ascending=False).head(15)
    top15["Direction"] = top15["Coefficient"].apply(lambda x: "Increases Risk" if x > 0 else "Decreases Risk")
    top15["Feature"]   = top15["Feature"].map(lambda f: FRIENDLY.get(f, f))
    top15 = top15.sort_values("abs")
    fig = px.bar(top15, x="Coefficient", y="Feature", orientation="h", color="Direction",
                 color_discrete_map={"Increases Risk": AF_COLOR, "Decreases Risk": NO_AF_COLOR},
                 title="Top 15 Feature Importances")
    fig.update_layout(yaxis_title="", legend=dict(orientation="h", y=-0.18),
                      height=340, margin=dict(t=50,b=60,l=20,r=20), **BASE)
    st.plotly_chart(fig, use_container_width=True)

# ── Model comparison table ────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">4-Model Comparison</div>', unsafe_allow_html=True)
st.caption("Replicating the experiment from model_experiments.py — same train/test split.")

@st.cache_data
def compute_comparison():
    # Reduced features (top 25 by coef magnitude)
    coef_series = pd.Series(model.coef_[0], index=X_train.columns).abs().sort_values(ascending=False)
    top_feats   = coef_series.head(25).index.tolist()
    sc_red = StandardScaler()
    Xtr_red = sc_red.fit_transform(X_train[top_feats])
    Xte_red = sc_red.transform(X_test[top_feats])
    m_red   = LogisticRegression(max_iter=5000, class_weight="balanced").fit(Xtr_red, y_train)

    m_base = LogisticRegression(max_iter=5000).fit(X_train_scaled, y_train)

    configs = {
        "Baseline LR":              (m_base, X_test_scaled, 0.5),
        "Balanced LR ✓":            (model,  X_test_scaled, 0.5),
        "Balanced + Threshold 0.3": (model,  X_test_scaled, 0.3),
        "Reduced Features (25)":    (m_red,  Xte_red,       0.5),
    }
    rows = []
    for name, (m, Xte, thresh) in configs.items():
        probs = m.predict_proba(Xte)[:, 1]
        preds = (probs >= thresh).astype(int)
        fpr_m, tpr_m, _ = roc_curve(y_test, probs)
        rows.append({
            "Model":     name,
            "Accuracy":  f"{accuracy_score(y_test, preds):.1%}",
            "Precision": f"{precision_score(y_test, preds, zero_division=0):.1%}",
            "Recall":    f"{recall_score(y_test, preds):.1%}",
            "F1":        f"{f1_score(y_test, preds, zero_division=0):.1%}",
            "AUC":       f"{auc(fpr_m, tpr_m):.3f}",
        })
    return pd.DataFrame(rows).set_index("Model")

with st.spinner("Computing model comparison…"):
    comp_df = compute_comparison()

st.dataframe(comp_df, use_container_width=True)
st.caption("✓ = Selected model used in Risk Assessment. Balanced LR trades precision for recall — clinically appropriate.")
