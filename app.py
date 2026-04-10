import streamlit as st
from utils import inject_css

st.set_page_config(
    page_title="AF Risk DSS",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🫀 AF Risk DSS")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py",                        label="🏠 Home")
st.sidebar.page_link("pages/1_Risk_Assessment.py",    label="🔍 Risk Assessment")
st.sidebar.page_link("pages/2_EDA.py",                label="📊 EDA")
st.sidebar.page_link("pages/3_Model_Performance.py",  label="📈 Model Performance")
st.sidebar.page_link("pages/4_What_If.py",            label="🔬 What-If Analysis")
st.sidebar.markdown("---")

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🫀 Atrial Fibrillation Risk DSS</h1>
    <p>A clinical decision support system for predicting in-hospital AF risk in post-MI patients</p>
</div>
""", unsafe_allow_html=True)

# ── Key stats ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, val, label in zip(
    [c1, c2, c3, c4],
    ["1,700", "10%", "35", "8"],
    ["Patient Records", "AF Incidence Rate", "Clinical Predictors", "Database Tables"],
):
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{val}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

# ── About ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">About This System</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([3, 2])
with col_a:
    st.write("""
    This Decision Support System helps clinicians assess the risk of **atrial fibrillation (AF)**
    developing in patients hospitalized following a **myocardial infarction (MI)**.

    AF is one of the most clinically significant complications of MI, occurring in 4–25% of patients
    during the acute phase and associated with a **40% increase in mortality** compared to MI alone.
    Early identification enables timely rhythm monitoring and preventive intervention.

    The system uses a **balanced logistic regression model** trained on 1,700 patient records from
    the UCI MI Complications dataset, predicting AF probability from 35 admission and history
    variables — stratifying patients into Low, Medium, or High risk with tailored recommendations.
    """)
    st.markdown("""
    <div class="info-box">
        ⚕️ <strong>Clinical context:</strong> Preventive strategies for high-risk patients include
        continuous ECG monitoring, early reperfusion therapy, and electrolyte management
        (potassium and magnesium). This DSS supports — not replaces — clinical judgement.
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("**Data Source**")
    st.write(
        "UCI Machine Learning Repository — Myocardial Infarction Complications dataset "
        "(Krasnoyarsk Interdistrict Clinical Hospital, 1992–1995). ~1,700 patients, 124 raw variables."
    )
    st.markdown("**Model**")
    st.write(
        "Logistic regression with `class_weight='balanced'` to handle the 10:1 class imbalance. "
        "Recall ≈ 0.49 | AUC ≈ 0.73."
    )
    st.markdown("**Database**")
    st.write(
        "PostgreSQL hosted on Supabase — 8 normalized tables linked by `patient_id`. "
        "Raw values stored as NULL (no imputation); imputation applied in the analytics pipeline."
    )
    st.markdown("**Stakeholders**")
    st.write("Cardiologists, hospitalists, and nursing staff in acute MI care settings.")

# ── Navigation guide ──────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Navigate the App</div>', unsafe_allow_html=True)

pages = [
    ("🔍", "Risk Assessment",    "Look up any patient by ID and get a real-time AF risk prediction with a probability gauge and clinical recommendation."),
    ("📊", "EDA",                "Explore the dataset through interactive charts — class distribution, demographics, vitals, and risk factor breakdowns."),
    ("📈", "Model Performance",  "Evaluate the model with a confusion matrix, ROC curve, precision-recall curve, and a 4-model comparison table."),
    ("🔬", "What-If Analysis",   "Adjust a patient's clinical parameters interactively and see how their AF risk score changes in real time."),
]
cols = st.columns(4)
for col, (icon, title, desc) in zip(cols, pages):
    col.markdown(f"""
    <div class="nav-card">
        <h3>{icon} {title}</h3>
        <p>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div class="info-box">👈 Use the <strong>sidebar</strong> on the left to navigate between pages.</div>',
    unsafe_allow_html=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    "Healthcare DSS · Built with Streamlit + PostgreSQL (Supabase) · "
    "Data: UCI MI Complications Dataset · Model: Balanced Logistic Regression"
)
