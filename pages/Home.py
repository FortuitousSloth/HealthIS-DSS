import streamlit as st
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
from utils import inject_css

inject_css()


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
    ["1,700", "10%", "35", "10"],
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
    developing in patients hospitalized after a **myocardial infarction (MI)**.

    AF is one of the most serious complications of MI, showing up in 4–25% of patients during
    the acute phase. It's linked to a **40% increase in mortality** compared to MI alone, so
    catching it early gives clinicians a real window to act.

    The system runs a **regularized logistic regression model** trained on 1,700 patient records
    from the UCI MI Complications dataset. It takes 35 admission and history variables as input
    and outputs an AF probability score, grouping patients into Low, Medium, or High risk
    with a matching clinical recommendation.
    """)
    st.markdown("""
    <div class="info-box">
        ⚕️ <strong>Clinical context:</strong> For high-risk patients, common preventive steps include
        continuous ECG monitoring, early reperfusion therapy, and keeping electrolytes like potassium
        and magnesium in check. This tool is meant to support clinical judgment, not replace it.
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("**Data Source**")
    st.write(
        "UCI Machine Learning Repository, Myocardial Infarction Complications dataset "
        "(Krasnoyarsk Interdistrict Clinical Hospital, 1992–1995). About 1,700 patients across 124 raw variables."
    )
    st.markdown("**Model**")
    st.write(
        "Logistic regression with `class_weight='balanced'`, L2 regularization (C=0.05), "
        "and a decision threshold of 0.30 to prioritize recall. Recall is around 57% with an AUC of 0.61."
    )
    st.markdown("**Database**")
    st.write(
        "PostgreSQL hosted on Supabase with 10 normalized tables, all linked by `patient_id`. "
        "Includes clinical code mappings (LOINC/ICD-10) and a provider table. Raw values are stored as-is and imputation happens in the analytics layer."
    )
    st.markdown("**Stakeholders**")
    st.write("Cardiologists, hospitalists, and nursing staff in acute MI care settings.")

# ── Navigation guide ──────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Navigate the App</div>', unsafe_allow_html=True)

pages = [
    ("🔍", "Risk Assessment",   "Look up any patient by ID and get a real-time AF risk prediction with a probability gauge and clinical recommendation.", "pages/1_Risk_Assessment.py"),
    ("📊", "EDA",               "Explore the dataset with interactive charts covering class distribution, demographics, vitals, and key risk factors.",    "pages/2_EDA.py"),
    ("📈", "Model Performance", "Review model results including a confusion matrix, ROC curve, precision-recall curve, and a comparison across model configurations.", "pages/3_Model_Performance.py"),
    ("🔬", "What-If Analysis",  "Tweak a patient's clinical parameters and see how the AF risk score responds in real time.",                             "pages/4_What_If.py"),
]

st.markdown("""
<style>
div[data-testid="stPageLink"] a {
    background: #f0f4ff;
    color: #1E3A5F !important;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-size: 0.84rem;
    font-weight: 600;
    text-decoration: none !important;
    display: block;
    text-align: center;
    margin-top: 0.8rem;
    border: 1.5px solid #c7d4f0;
    letter-spacing: 0.01em;
    transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}
div[data-testid="stPageLink"] a:hover {
    background: #1E3A5F;
    color: white !important;
    border-color: #1E3A5F;
}
</style>
""", unsafe_allow_html=True)

cols = st.columns(4)
for col, (icon, title, desc, path) in zip(cols, pages):
    with col:
        st.markdown(f"""
        <div class="nav-card">
            <h3>{icon} {title}</h3>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(path, label=f"Open {title}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    "Healthcare DSS · Built with Streamlit + PostgreSQL (Supabase) · "
    "Data: UCI MI Complications Dataset · Model: Balanced LR (C=0.05, threshold=0.30)"
)
