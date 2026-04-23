import streamlit as st

st.set_page_config(
    page_title="AF Risk DSS",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Login gate ────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer { visibility: hidden; }

    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 3rem 3.5rem;
        box-shadow: 0 8px 40px rgba(30,58,95,0.15);
        max-width: 420px;
        width: 100%;
        border-top: 5px solid #1E3A5F;
        text-align: center;
    }
    .login-logo { font-size: 3rem; margin-bottom: 0.5rem; }
    .login-title {
        font-size: 1.6rem; font-weight: 700;
        color: #1E3A5F; margin-bottom: 0.25rem;
    }
    .login-subtitle {
        font-size: 0.88rem; color: #6B7280;
        margin-bottom: 2rem; line-height: 1.5;
    }
    .hipaa-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1E40AF;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        letter-spacing: 0.04em;
        border: 1px solid #BFDBFE;
    }
    .login-footer {
        font-size: 0.75rem; color: #9CA3AF;
        margin-top: 1.5rem; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">🫀</div>
            <div class="login-title">AF Risk DSS</div>
            <div class="login-subtitle">Atrial Fibrillation Clinical Decision Support</div>
            <div class="hipaa-badge">🔒 HIPAA-Compliant Access</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Provider Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        login_btn = st.button("Sign In", type="primary", use_container_width=True)

        st.markdown("""
        <div class="login-footer">
            Access to this system is restricted to authorized clinical personnel.<br>
            All activity is logged for compliance purposes.
        </div>
        """, unsafe_allow_html=True)

        if login_btn:
            if username.strip() and password.strip():
                st.session_state["logged_in"] = True
                st.session_state["username"] = username.strip()
                st.rerun()
            else:
                st.error("Please enter both a username and password.")

# ── App routing ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in", False):
    show_login()
else:
    # Logout button in sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0.6rem 0.8rem; background:#EFF6FF; border-radius:10px;
                    border-left:3px solid #1E3A5F; margin-bottom:1rem; font-size:0.85rem;">
            <span style="color:#6B7280;">Signed in as</span><br>
            <strong style="color:#1E3A5F;">{st.session_state.get('username','')}</strong>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()
        st.markdown("---")

    pg = st.navigation([
        st.Page("pages/Home.py",                   title="Home",             icon="🏠", default=True),
        st.Page("pages/1_Risk_Assessment.py",       title="Risk Assessment",  icon="🔍"),
        st.Page("pages/2_EDA.py",                   title="EDA",              icon="📊"),
        st.Page("pages/3_Model_Performance.py",     title="Model Performance",icon="📈"),
        st.Page("pages/4_What_If.py",               title="What-If Analysis", icon="🔬"),
    ])
    pg.run()
