import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import joblib
import numpy as np
import os
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from database_config import engine
from disease_info import get_disease_info, format_disease_info

# --- PREMIUM DASHBOARD CONFIGURATION ---
st.set_page_config(
    page_title="CareFlow AI | Professional Healthcare Suite", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Plotly Template for a Premium Look — updated dynamically with theme
_is_dark = st.session_state.get("dark_mode", False)
_paper_bg = 'rgba(30,41,59,0)' if _is_dark else 'rgba(0,0,0,0)'
_font_color = '#e2e8f0' if _is_dark else '#2c3e50'
_grid_color = '#334155' if _is_dark else '#f0f2f6'

careflow_theme = go.layout.Template(
    layout=go.Layout(
        colorway=['#4facfe', '#00f2fe', '#38ef7d', '#ff9a9e', '#f6d365', '#a18cd1'],
        paper_bgcolor=_paper_bg,
        plot_bgcolor=_paper_bg,
        font=dict(family='Inter, sans-serif', size=12, color=_font_color),
        xaxis=dict(gridcolor=_grid_color, linecolor=_grid_color),
        yaxis=dict(gridcolor=_grid_color, linecolor=_grid_color),
        margin=dict(l=20, r=20, t=40, b=20)
    )
)
pio.templates['careflow'] = careflow_theme
pio.templates.default = 'careflow'

# --- THEME INITIALIZATION ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- THEME CSS DEFINITIONS ---
LIGHT_THEME = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Montserrat:wght@700&display=swap');

    :root {
        --bg-primary: #f8fbff;
        --bg-secondary: #ffffff;
        --bg-card: #ffffff;
        --text-primary: #1a2a40;
        --text-secondary: #6b7280;
        --border-color: #eee;
        --sidebar-bg: #ffffff;
        --input-bg: #f9fafb;
        --input-border: #d1d5db;
        --metric-shadow: rgba(0, 50, 100, 0.05);
        --metric-shadow-hover: rgba(0, 50, 100, 0.1);
        --grid-color: #f0f2f6;
    }

    .main, .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary) !important;
    }

    .stMetric {
        background-color: var(--bg-card);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px var(--metric-shadow);
        border: 1px solid rgba(0,0,0,0.03);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px var(--metric-shadow-hover);
    }

    .hero-banner {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 114, 255, 0.2);
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #00f2fe 0%, #4facfe 100%);
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    }

    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color);
    }

    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        color: var(--text-primary);
    }

    /* Inputs */
    input, textarea, select {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--input-border) !important;
    }

    /* Theme toggle badge */
    .theme-badge {
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    </style>
"""

DARK_THEME = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Montserrat:wght@700&display=swap');

    :root {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-card: #1e293b;
        --text-primary: #e2e8f0;
        --text-secondary: #94a3b8;
        --border-color: #334155;
        --sidebar-bg: #1e293b;
        --input-bg: #0f172a;
        --input-border: #475569;
        --metric-shadow: rgba(0, 0, 0, 0.3);
        --metric-shadow-hover: rgba(0, 0, 0, 0.5);
        --grid-color: #1e293b;
    }

    .main, .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary) !important;
    }

    /* Override Streamlit's default white backgrounds */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    section[data-testid="stSidebar"] > div,
    .block-container {
        background-color: var(--bg-primary) !important;
    }

    .stMetric {
        background-color: var(--bg-card) !important;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px var(--metric-shadow);
        border: 1px solid var(--border-color);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px var(--metric-shadow-hover);
    }
    .stMetric label, .stMetric [data-testid="stMetricLabel"],
    .stMetric [data-testid="stMetricValue"], .stMetric [data-testid="stMetricDelta"] {
        color: var(--text-primary) !important;
    }

    .hero-banner {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 114, 255, 0.3);
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #00f2fe 0%, #4facfe 100%);
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    }

    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
    }

    /* Inputs */
    input, textarea, select,
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] select {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--input-border) !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-secondary) !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #4facfe !important;
        border-bottom-color: #4facfe !important;
    }

    /* Alerts / Info boxes */
    .stAlert {
        background-color: var(--bg-card) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }

    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: var(--bg-card) !important;
    }

    /* Divider */
    hr {
        border-color: var(--border-color) !important;
    }

    /* Theme toggle badge */
    .theme-badge {
        background: #1e3a5f;
        color: #93c5fd;
        border: 1px solid #2563eb;
    }
    </style>
"""

# Inject the active theme
if st.session_state.dark_mode:
    st.markdown(DARK_THEME, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_THEME, unsafe_allow_html=True)

# --- AUTHENTICATION & LOGIN UI ---
# Load configuration
if not os.path.exists('auth_config.yaml'):
    st.error("Authentication configuration missing. Please check auth_config.yaml.")
    st.stop()
    
with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=False
)

# Professional Login UI Styling
if st.session_state.get("authentication_status") is not True:
    _login_dark = st.session_state.get("dark_mode", False)
    _login_bg = "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)" if _login_dark else "linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 50%, #cbd5e1 100%)"
    _form_bg = "linear-gradient(145deg, #1e293b 0%, #0f172a 100%)" if _login_dark else "linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)"
    _form_border = "#334155" if _login_dark else "#e2e8f0"
    _input_bg = "#0f172a" if _login_dark else "#f9fafb"
    _input_border = "#475569" if _login_dark else "#d1d5db"
    _label_color = "#e2e8f0" if _login_dark else "#1f2937"
    _h1_color = "#e2e8f0" if _login_dark else "#1f2937"
    _p_color = "#94a3b8" if _login_dark else "#6b7280"
    _input_text = "#e2e8f0" if _login_dark else "#1f2937"

    st.markdown(f"""
        <style>
            .stApp, .main {{
                background: {_login_bg} !important;
                min-height: 100vh !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }}

            [data-testid="stForm"] {{
                background: {_form_bg} !important;
                padding: 60px !important;
                border-radius: 20px !important;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2), 0 8px 32px rgba(0, 0, 0, 0.12) !important;
                max-width: 500px !important;
                margin: 40px auto !important;
                border: 2px solid {_form_border} !important;
                border-top: 6px solid #dc2626 !important;
                position: relative !important;
                backdrop-filter: blur(10px) !important;
            }}

            [data-testid="stForm"]::before {{
                content: "⚕️" !important;
                position: absolute !important;
                top: 25px !important;
                right: 25px !important;
                font-size: 2.5rem !important;
                opacity: 0.08 !important;
            }}

            [data-testid="stForm"] input {{
                border-radius: 10px !important;
                border: 2px solid {_input_border} !important;
                padding: 16px 18px !important;
                font-size: 16px !important;
                background-color: {_input_bg} !important;
                color: {_input_text} !important;
                transition: all 0.3s ease !important;
                margin-bottom: 16px !important;
                font-family: inherit !important;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            }}

            [data-testid="stForm"] input:focus {{
                border-color: #dc2626 !important;
                outline: none !important;
                box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1), inset 0 1px 3px rgba(0, 0, 0, 0.1) !important;
                background-color: {_input_bg} !important;
                transform: translateY(-1px) !important;
            }}

            [data-testid="stForm"] button[data-testid="stBaseButton-secondary"] {{
                width: 100% !important;
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
                color: white !important;
                border-radius: 12px !important;
                height: 56px !important;
                font-weight: 700 !important;
                font-size: 18px !important;
                border: none !important;
                margin-top: 32px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                letter-spacing: 0.025em !important;
                box-shadow: 0 8px 25px rgba(220, 38, 38, 0.3) !important;
                text-transform: uppercase !important;
            }}

            [data-testid="stForm"] button[data-testid="stBaseButton-secondary"]:hover {{
                background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 12px 35px rgba(220, 38, 38, 0.4) !important;
            }}

            .stAlert {{
                border-radius: 12px !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
                margin-top: 24px !important;
                border-left: 5px solid #dc2626 !important;
                background: linear-gradient(90deg, #fef2f2 0%, #ffffff 100%) !important;
            }}

            .stAlert > div {{
                padding: 16px 20px !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                color: #991b1b !important;
            }}

            [data-testid="stForm"] label {{
                font-weight: 700 !important;
                color: {_label_color} !important;
                font-size: 15px !important;
                margin-bottom: 8px !important;
                display: block !important;
                letter-spacing: 0.025em !important;
                text-transform: uppercase !important;
            }}

            .doctor-header {{
                text-align: center !important;
                margin-bottom: 40px !important;
                position: relative !important;
            }}

            .doctor-header .icon {{
                font-size: 5rem !important;
                margin-bottom: 20px !important;
                display: block !important;
                filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1)) !important;
            }}

            .doctor-header h1 {{
                color: {_h1_color} !important;
                font-size: 32px !important;
                font-weight: 800 !important;
                margin: 0 0 12px 0 !important;
                letter-spacing: -0.025em !important;
            }}

            .doctor-header p {{
                color: {_p_color} !important;
                font-size: 18px !important;
                margin: 0 !important;
                font-weight: 500 !important;
            }}

            .doctor-header .badge {{
                position: absolute !important;
                top: 0 !important;
                right: 0 !important;
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
                color: #1e40af !important;
                padding: 6px 16px !important;
                border-radius: 25px !important;
                font-size: 13px !important;
                font-weight: 700 !important;
                border: 2px solid #93c5fd !important;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2) !important;
            }}

            .security-indicators {{
                display: flex !important;
                justify-content: center !important;
                gap: 20px !important;
                margin-top: 30px !important;
                opacity: 0.7 !important;
            }}

            .security-indicators .indicator {{
                display: flex !important;
                align-items: center !important;
                gap: 6px !important;
                font-size: 12px !important;
                color: {_p_color} !important;
                font-weight: 500 !important;
            }}
        </style>

        <div class="doctor-header">
            <span class="icon">🏥</span>
            <h1>Elite Medical Portal</h1>
            <p>Advanced Healthcare Professional Platform</p>
            <div class="badge">HIPAA & SOC2 Compliant</div>
        </div>

        <div class="security-indicators">
            <div class="indicator">🔒 SSL Encrypted</div>
            <div class="indicator">🛡️ Multi-Factor Auth</div>
            <div class="indicator">📋 Audit Trail</div>
        </div>
    """, unsafe_allow_html=True)

# Render login component
try:
    authenticator.login()
except Exception as e:
    st.error(f"Authentication Error: {e}")

if st.session_state.get("authentication_status") is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning('Please enter your username and password to access clinical data.')
    st.stop()

# --- DATA LAYER ---
@st.cache_data
def load_data():
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query("SELECT * FROM ClinicalData", conn)
        
        if 'DateofAdmission' in df.columns:
            df['DateofAdmission'] = pd.to_datetime(df['DateofAdmission'])
        if 'DischargeDate' in df.columns:
            df['DischargeDate'] = pd.to_datetime(df['DischargeDate'])
        
        # Add synthetic PatientID column using index
        df['PatientID'] = df.index.map(lambda x: f"PAT{x+1:04d}")
        
        return df
    except Exception as e:
        st.error(f"Error loading healthcare data: {e}")
        return None

df = load_data()

# --- SIDEBAR NAVIGATION (POLISHED) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)
    st.title("CareFlow AI")
    
    st.markdown(f"""
        <div style="background: #f0f7ff; padding: 15px; border-radius: 12px; border-left: 4px solid #4facfe; margin-bottom: 20px;">
            <p style="margin: 0; color: #1a2a40; font-weight: 600;">Signed in as</p>
            <p style="margin: 0; color: #4facfe; font-size: 14px;">{st.session_state['name']}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- DARK / LIGHT MODE TOGGLE ---
    theme_icon = "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"
    if st.button(theme_icon, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.divider()

    page = st.radio("MAIN NAVIGATION", [
        "📈 Executive Analytics", 
        "🧠 AI Diagnostic Center", 
        "👥 Patient Dashboard", 
        "📋 Medical Records", 
        "📅 Appointments", 
        "💊 Prescriptions",
        "🗺️ Hospital Locations",
        "👨‍⚕️ Doctor Schedule"
    ], index=0)
    st.divider()
    
    # Advanced Filters
    if page == "📈 Executive Analytics":
        st.subheader("⚙️ Filter Suite")
        medical_condition = st.multiselect("Medical Condition", options=df["MedicalCondition"].unique(), default=df["MedicalCondition"].unique())
        gender = st.multiselect("Patient Gender", options=df["Gender"].unique(), default=df["Gender"].unique())
        admission_type = st.multiselect("Admission Mode", options=df["AdmissionType"].unique(), default=df["AdmissionType"].unique())
    
    st.divider()
    authenticator.logout('Logout System', 'sidebar')

# Apply Filters for Analytics
if page == "📈 Executive Analytics":
    df_selection = df.query("MedicalCondition == @medical_condition & Gender == @gender & AdmissionType == @admission_type")
else:
    df_selection = df

# --- PAGE 1: EXECUTIVE ANALYTICS ---
if page == "📈 Executive Analytics":
    # Hero Banner
    st.markdown(f"""
        <div class="hero-banner">
            <h1 style="color: white; margin: 0; font-size: 2.2rem;">Healthcare Performance Hub</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                Welcome back, {st.session_state['name']}. Here is a summary of active patient metrics and hospital efficiency.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Active Patients", f"{len(df_selection):,}", delta="Live")
    with col2:
        avg_billing = df_selection["BillingAmount"].mean()
        st.metric("Avg Billing Amount", f"${avg_billing:,.0f}", delta=f"{len(df_selection) // 100}% Vol", delta_color="normal")
    with col3:
        avg_stay = df_selection["LengthOfStay"].mean()
        st.metric("Avg Stay Duration", f"{avg_stay:.1f} Days", delta="-0.4", delta_color="inverse")
    with col4:
        unique_hosps = df_selection["Hospital"].nunique()
        st.metric("Reporting Facilities", f"{unique_hosps}", delta="Active")

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Charts Row 1
    r1c1, r1c2 = st.columns([1, 1.2])
    with r1c1:
        st.subheader("🏥 Condition Breakdown")
        fig_condition = px.bar(
            df_selection.groupby("MedicalCondition").size().reset_index(name="Count"),
            x="Count", y="MedicalCondition", orientation='h', color='Count',
            color_continuous_scale='Blues'
        )
        fig_condition.update_layout(yaxis_title=None, xaxis_title="Patient Volume")
        st.plotly_chart(fig_condition, use_container_width=True)

    with r1c2:
        st.subheader("💰 Revenue vs Age Correlation")
        fig_age_billing = px.scatter(
            df_selection.sample(min(2000, len(df_selection))),
            x="Age", y="BillingAmount", color="AdmissionType",
            hover_data=["MedicalCondition"], opacity=0.7,
            marginal_x="histogram", trendline="ols"
        )
        st.plotly_chart(fig_age_billing, use_container_width=True)

    # Row 2
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.subheader("🛡️ Insurance Market Share")
        fig_insurance = px.pie(df_selection, names="InsuranceProvider", hole=0.6)
        st.plotly_chart(fig_insurance, use_container_width=True)

    with r2c2:
        st.subheader("⏳ Efficiency by Condition")
        fig_stay = px.box(df_selection, x="MedicalCondition", y="LengthOfStay", color="MedicalCondition")
        st.plotly_chart(fig_stay, use_container_width=True)

    with st.expander("🔎 Audit Raw Clinical Records (Top 100)"):
        st.dataframe(df_selection.head(100), use_container_width=True)

# --- PAGE 2: AI DIAGNOSTIC CENTER ---
elif page == "🧠 AI Diagnostic Center":
    st.markdown(f"""
        <div class="hero-banner" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h1 style="color: white; margin: 0; font-size: 2.2rem;">AI Diagnostic Intelligence</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1rem;">
                Advanced machine learning risk profiling for preventative care and early intervention.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Load Model Assets
    try:
        model = joblib.load('disease_model.pkl')
        le_gender = joblib.load('le_gender.pkl')
        le_blood = joblib.load('le_blood.pkl')
        le_condition = joblib.load('le_condition.pkl')
        metadata = joblib.load('model_metadata.pkl')
    except Exception as e:
        st.warning("Prediction model not found. System needs training.")
        st.stop()

    col1, col2 = st.columns([1, 1.8])

    with col1:
        st.markdown('<h3 style="margin-bottom:20px;">👤 Patient Intake</h3>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<br>", unsafe_allow_html=True)
            age = st.slider("Patient Age", 0, 100, 45)
            gender = st.selectbox("Recorded Gender", options=metadata['genders'])
            blood_type = st.selectbox("Primary Blood Group", options=metadata['blood_types'])
            st.markdown("<br>", unsafe_allow_html=True)
            predict_btn = st.button("EXECUTE NEURAL RISK ANALYSIS")

    with col2:
        if predict_btn:
            # Prepare input
            gender_encoded = le_gender.transform([gender])[0]
            blood_encoded = le_blood.transform([blood_type])[0]
            input_data = np.array([[age, gender_encoded, blood_encoded]])
            
            # Predict
            probs = model.predict_proba(input_data)[0]
            prediction_df = pd.DataFrame({'Condition': le_condition.classes_, 'Prob': probs * 100}).sort_values('Prob', ascending=False)
            top_condition = prediction_df.iloc[0]['Condition']
            top_prob = prediction_df.iloc[0]['Prob']

            st.markdown(f"#### Results for Age {age} ({gender})")
            
            if top_prob > 20:
                st.error(f"**Primary Risk Detected:** {top_condition} ({top_prob:.1f}%)")
            else:
                st.success(f"**Primary Profile:** {top_condition} ({top_prob:.1f}%)")

            # Chart
            fig_probs = px.bar(prediction_df, x='Prob', y='Condition', color='Prob', color_continuous_scale='Purples', range_x=[0, 100])
            fig_probs.update_layout(showlegend=False, height=350, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_probs, use_container_width=True)
            
            st.info(f"💡 **AI Clinical Note**: The diagnostic patterns indicate a predisposition toward {top_condition}. Suggest screening and follow-up.")
            
            # --- DISEASE SYMPTOMS & RECOMMENDATIONS ---
            st.markdown("---")
            st.markdown("<h3 style='color: #667eea;'>🏥 Detailed Disease Information</h3>", unsafe_allow_html=True)
            
            disease_info = get_disease_info(top_condition)
            
            if disease_info:
                # Create three columns for better layout
                col_sym, col_mgmt, col_life = st.columns(3)
                
                with col_sym:
                    st.markdown(f"<div style='background: #fff3cd; padding: 20px; border-radius: 12px; border-left: 4px solid #ffc107;'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top: 0; color: #856404;'>🔍 Symptoms (लक्षण)</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #856404; font-size: 0.9rem;'><strong>Risk Level:</strong> {disease_info['risk_level']}</p>", unsafe_allow_html=True)
                    for symptom in disease_info['symptoms']:
                        st.markdown(f"- {symptom}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_mgmt:
                    st.markdown(f"<div style='background: #d1ecf1; padding: 20px; border-radius: 12px; border-left: 4px solid #17a2b8;'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top: 0; color: #0c5460;'>💊 Management & Treatment (उपचार)</h4>", unsafe_allow_html=True)
                    for mgmt in disease_info['management']:
                        st.markdown(f"- {mgmt}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_life:
                    st.markdown(f"<div style='background: #d4edda; padding: 20px; border-radius: 12px; border-left: 4px solid #28a745;'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='margin-top: 0; color: #155724;'>🌿 Lifestyle Tips (जीवनशैली)</h4>", unsafe_allow_html=True)
                    for lifestyle in disease_info['lifestyle']:
                        st.markdown(f"- {lifestyle}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Additional recommendations section
                st.markdown("<br>", unsafe_allow_html=True)
                st.warning(f"""
                    ⚠️ **Important Medical Disclaimer:** This AI analysis is for informational purposes only and should not be considered medical advice. 
                    Please consult with qualified healthcare professionals for proper diagnosis and treatment of {top_condition}. 
                    Regular check-ups with your physician are strongly recommended.
                """)
            else:
                st.warning(f"Detailed information for {top_condition} is not yet available in the database.")
        else:
            st.markdown("""
                <div style="background: #ffffff; padding: 40px; border-radius: 16px; border: 2px dashed #ddd; text-align: center; color: #888;">
                    <p style="font-size: 1.2rem;">Ready for Analysis</p>
                    <p>Enter patient particulars and click 'Execute' to begin the neural diagnostic process.</p>
                </div>
            """, unsafe_allow_html=True)

# --- PAGE 3: PATIENT DASHBOARD ---
elif page == "👥 Patient Dashboard":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">👥 Patient Management Hub</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Comprehensive patient overview and quick actions</p>
        </div>
    """, unsafe_allow_html=True)

    # Patient Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Patients", len(df_selection), "🟢 Stable")
    with col2:
        critical_count = len(df_selection[df_selection["MedicalCondition"].isin(["Cancer", "Heart Disease", "Stroke"])])
        st.metric("Critical Cases", critical_count, "🔴 Monitor")
    with col3:
        today_admissions = len(df_selection[df_selection["DateofAdmission"].dt.date == pd.Timestamp.today().date()])
        st.metric("Today's Admissions", today_admissions, "📅 New")
    with col4:
        avg_age = df_selection["Age"].mean()
        st.metric("Average Age", f"{avg_age:.1f}", "👴 Population")

    # Patient List with Actions
    st.markdown("### 📋 Active Patient List")
    st.markdown("---")

    # --- FEATURE 1: PATIENT RISK SCORE SECTION ---
    st.markdown("### 🎯 Patient Risk Score Analysis")
    
    def calc_risk(patient_row):
        score = 0
        age = patient_row.get("Age", 0)
        if age > 70: score += 30
        elif age > 60: score += 20
        elif age > 50: score += 10
        
        condition = patient_row.get("MedicalCondition", "")
        if condition in ["Cancer", "Heart Disease", "Stroke"]: score += 40
        elif condition in ["Diabetes", "Hypertension", "COPD"]: score += 25
        elif condition in ["Kidney Disease", "Liver Disease"]: score += 30
        
        stay = patient_row.get("LengthOfStay", 0)
        if stay > 14: score += 15
        elif stay > 7: score += 10
        
        billing = patient_row.get("BillingAmount", 0)
        if billing > 30000: score += 15
        elif billing > 20000: score += 10
        
        adm = patient_row.get("AdmissionType", "")
        if adm == "Emergency": score += 20
        elif adm == "Urgent": score += 10
        
        score = min(score, 100)
        if score >= 70: return score, "Critical", "#ef4444", "🔴"
        elif score >= 50: return score, "High", "#f59e0b", "🟠"
        elif score >= 30: return score, "Medium", "#eab308", "🟡"
        else: return score, "Low", "#10b981", "🟢"

    # Risk score summary
    risk_sample = df_selection.head(200)
    risk_results = risk_sample.apply(lambda r: calc_risk(r.to_dict()), axis=1)
    risk_df = pd.DataFrame(risk_results.tolist(), columns=["Score", "Level", "Color", "Icon"])
    risk_df["Name"] = risk_sample["Name"].values
    risk_df["Condition"] = risk_sample["MedicalCondition"].values
    risk_df["Age"] = risk_sample["Age"].values
    risk_df["Doctor"] = risk_sample["Doctor"].values

    # Risk distribution metrics
    rk1, rk2, rk3, rk4 = st.columns(4)
    rk1.metric("🔴 Critical", len(risk_df[risk_df["Level"] == "Critical"]))
    rk2.metric("🟠 High Risk", len(risk_df[risk_df["Level"] == "High"]))
    rk3.metric("🟡 Medium Risk", len(risk_df[risk_df["Level"] == "Medium"]))
    rk4.metric("🟢 Low Risk", len(risk_df[risk_df["Level"] == "Low"]))

    # Risk distribution chart
    rc1, rc2 = st.columns([1, 1.5])
    with rc1:
        risk_counts = risk_df["Level"].value_counts().reset_index()
        risk_counts.columns = ["Level", "Count"]
        fig_risk_pie = px.pie(
            risk_counts, names="Level", values="Count",
            color="Level",
            color_discrete_map={"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#eab308", "Low": "#10b981"},
            hole=0.5, title="Risk Level Distribution"
        )
        fig_risk_pie.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_risk_pie, use_container_width=True)

    with rc2:
        fig_risk_bar = px.histogram(
            risk_df, x="Score", nbins=20,
            color_discrete_sequence=["#667eea"],
            title="Risk Score Distribution"
        )
        fig_risk_bar.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_risk_bar, use_container_width=True)

    # Top critical patients table
    st.markdown("#### 🚨 Top Critical Patients (Immediate Attention Required)")
    critical_patients = risk_df[risk_df["Level"].isin(["Critical", "High"])].sort_values("Score", ascending=False).head(10)
    if not critical_patients.empty:
        for _, row in critical_patients.iterrows():
            st.markdown(f"""
                <div style="background: white; padding: 14px 20px; margin: 6px 0; border-radius: 10px;
                            border-left: 5px solid {row['Color']}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #1f2937; font-size: 1rem;">{row['Icon']} {row['Name']}</strong>
                        <span style="color: #6b7280; font-size: 0.9rem; margin-left: 12px;">Age: {row['Age']} | {row['Condition']} | Dr. {row['Doctor']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {row['Color']}; color: white; padding: 5px 14px; border-radius: 20px; font-weight: bold; font-size: 0.9rem;">
                            {row['Level']} — {row['Score']}/100
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Active Patient List")

    # Create patient cards
    patients_per_row = 3
    patient_rows = [df_selection.iloc[i:i+patients_per_row] for i in range(0, len(df_selection), patients_per_row)]

    for row_idx, patient_row in enumerate(patient_rows):
        cols = st.columns(patients_per_row)
        for col_idx, (_, patient) in enumerate(patient_row.iterrows()):
            with cols[col_idx]:
                # Determine risk level
                risk_color = "#10b981"  # green
                risk_icon = "🟢"
                if patient["MedicalCondition"] in ["Cancer", "Heart Disease", "Stroke"]:
                    risk_color = "#ef4444"  # red
                    risk_icon = "🔴"
                elif patient["MedicalCondition"] in ["Diabetes", "Hypertension"]:
                    risk_color = "#f59e0b"  # yellow
                    risk_icon = "🟡"

                st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 12px; border-left: 4px solid {risk_color}; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0; color: #1f2937;">{patient['Name']}</h4>
                                <p style="margin: 5px 0; color: #6b7280; font-size: 0.9rem;">ID: {patient['PatientID']} • Age: {patient['Age']}</p>
                            </div>
                            <span style="font-size: 1.5rem;">{risk_icon}</span>
                        </div>
                        <div style="margin-top: 15px;">
                            <p style="margin: 0; color: #374151;"><strong>Condition:</strong> {patient['MedicalCondition']}</p>
                            <p style="margin: 5px 0; color: #374151;"><strong>Doctor:</strong> {patient['Doctor']}</p>
                            <p style="margin: 5px 0; color: #374151;"><strong>Room:</strong> {patient['RoomNumber']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button(f"📋 Records", key=f"records_{patient['PatientID']}_{row_idx}_{col_idx}"):
                        st.session_state.selected_patient = patient['PatientID']
                        st.rerun()
                with col_btn2:
                    if st.button(f"💊 Rx", key=f"rx_{patient['PatientID']}_{row_idx}_{col_idx}"):
                        st.session_state.selected_patient = patient['PatientID']
                        st.rerun()
                with col_btn3:
                    if st.button(f"📅 Appt", key=f"appt_{patient['PatientID']}_{row_idx}_{col_idx}"):
                        st.session_state.selected_patient = patient['PatientID']
                        st.rerun()

# --- PAGE 4: MEDICAL RECORDS ---
elif page == "📋 Medical Records":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">📋 Electronic Health Records</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Secure patient medical history and documentation</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Session state for new records ---
    if "new_records" not in st.session_state:
        st.session_state.new_records = []
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False
    if "show_report" not in st.session_state:
        st.session_state.show_report = False

    # --- Patient Search & Filter ---
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_term = st.text_input("🔍 Search Patients", placeholder="Enter patient name or ID...")
    with col_filter:
        record_filter = st.selectbox("Filter Records", ["All Records", "Recent Admissions", "Critical Cases", "Discharged"])

    # Merge DB records with newly added session records
    if st.session_state.new_records:
        new_df = pd.DataFrame(st.session_state.new_records)
        combined_df = pd.concat([df_selection, new_df], ignore_index=True)
    else:
        combined_df = df_selection.copy()

    # Apply record_filter
    if record_filter == "Critical Cases":
        combined_df = combined_df[combined_df["MedicalCondition"].isin(["Cancer", "Heart Disease", "Stroke"])]
    elif record_filter == "Recent Admissions":
        combined_df = combined_df.sort_values("DateofAdmission", ascending=False).head(50)

    # Apply search
    if search_term:
        filtered_df = combined_df[
            combined_df["Name"].str.contains(search_term, case=False, na=False) |
            combined_df["PatientID"].astype(str).str.contains(search_term, na=False)
        ]
    else:
        filtered_df = combined_df

    # --- Records Table ---
    st.markdown("### 📄 Patient Records")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[["PatientID", "Name", "Age", "Gender", "MedicalCondition", "Doctor", "DateofAdmission", "RoomNumber"]],
            use_container_width=True,
            column_config={
                "PatientID": st.column_config.TextColumn("Patient ID", width="small"),
                "Name": st.column_config.TextColumn("Patient Name", width="medium"),
                "Age": st.column_config.NumberColumn("Age", width="small"),
                "Gender": st.column_config.TextColumn("Gender", width="small"),
                "MedicalCondition": st.column_config.TextColumn("Condition", width="medium"),
                "Doctor": st.column_config.TextColumn("Doctor", width="medium"),
                "DateofAdmission": st.column_config.DateColumn("Admission Date", width="medium"),
                "RoomNumber": st.column_config.TextColumn("Room", width="small"),
            }
        )
    else:
        st.info("No records found matching your search criteria.")

    # --- Quick Action Buttons ---
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("➕ Add New Record", use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.session_state.show_report = False
            st.session_state.show_invoice = False
            st.session_state.show_pdf = False
    with col2:
        if st.button("📤 Export Records", use_container_width=True):
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"patient_records_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    with col3:
        if st.button("📄 Patient PDF", use_container_width=True):
            st.session_state.show_pdf = not st.session_state.get("show_pdf", False)
            st.session_state.show_add_form = False
            st.session_state.show_invoice = False
            st.session_state.show_report = False
    with col4:
        if st.button("🧾 Generate Invoice", use_container_width=True):
            st.session_state.show_invoice = not st.session_state.get("show_invoice", False)
            st.session_state.show_add_form = False
            st.session_state.show_report = False
            st.session_state.show_pdf = False
    with col5:
        if st.button("🔄 Sync with EHR", use_container_width=True):
            st.toast("✅ EHR sync completed successfully!", icon="🔄")
    with col6:
        if st.button("📊 Generate Report", use_container_width=True):
            st.session_state.show_report = not st.session_state.show_report
            st.session_state.show_add_form = False
            st.session_state.show_invoice = False
            st.session_state.show_pdf = False

    # =========================================================
    # FEATURE: PATIENT FULL INFO PDF DOWNLOAD
    # =========================================================
    if st.session_state.get("show_pdf", False):
        st.markdown("---")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        padding: 20px 30px; border-radius: 14px; color: white; margin-bottom: 20px;">
                <h3 style="margin:0;">📄 Patient Full Information — PDF Download</h3>
                <p style="margin:6px 0 0 0; opacity:0.85;">Generate a complete patient profile PDF with all medical details</p>
            </div>
        """, unsafe_allow_html=True)

        # Patient selector
        pdf_options = [f"{row['PatientID']} — {row['Name']} ({row['MedicalCondition']}, Age {row['Age']})"
                       for _, row in filtered_df.head(200).iterrows()]
        selected_pdf_patient = st.selectbox("👤 Select Patient", pdf_options, key="pdf_patient_select")

        if selected_pdf_patient:
            pid_pdf = selected_pdf_patient.split(" — ")[0]
            p = filtered_df[filtered_df["PatientID"] == pid_pdf].iloc[0]

            # Preview card
            def get_risk_for_pdf(patient_row):
                score = 0
                age = patient_row.get("Age", 0)
                if age > 70: score += 30
                elif age > 60: score += 20
                elif age > 50: score += 10
                cond = patient_row.get("MedicalCondition", "")
                if cond in ["Cancer", "Heart Disease", "Stroke"]: score += 40
                elif cond in ["Diabetes", "Hypertension", "COPD"]: score += 25
                elif cond in ["Kidney Disease", "Liver Disease"]: score += 30
                stay = patient_row.get("LengthOfStay", 0)
                if stay > 14: score += 15
                elif stay > 7: score += 10
                billing = patient_row.get("BillingAmount", 0)
                if billing > 30000: score += 15
                elif billing > 20000: score += 10
                adm = patient_row.get("AdmissionType", "")
                if adm == "Emergency": score += 20
                elif adm == "Urgent": score += 10
                score = min(score, 100)
                if score >= 70: return score, "Critical"
                elif score >= 50: return score, "High"
                elif score >= 30: return score, "Medium"
                else: return score, "Low"

            risk_score, risk_level = get_risk_for_pdf(p.to_dict())

            # Show preview
            prev_c1, prev_c2, prev_c3, prev_c4 = st.columns(4)
            prev_c1.metric("Patient", p["Name"])
            prev_c2.metric("Condition", p["MedicalCondition"])
            prev_c3.metric("Risk Level", risk_level)
            prev_c4.metric("Risk Score", f"{risk_score}/100")

            # PDF generation function
            def generate_patient_pdf(patient, risk_score, risk_level):
                import re
                from fpdf import FPDF

                def safe(text):
                    text = str(text) if text is not None else "N/A"
                    text = text.replace("\u2022", "-").replace("\u2013", "-").replace("\u2014", "-")
                    text = text.replace("\u2019", "'").replace("\u2018", "'")
                    text = text.replace("\u201c", '"').replace("\u201d", '"')
                    # Extract English parts from bilingual strings like "Hindi text (English text)"
                    paren_match = re.findall(r'\(([^)]+)\)', text)
                    latin_parts = []
                    for part in paren_match:
                        try:
                            part.encode('latin-1')
                            latin_parts.append(part.strip())
                        except:
                            pass
                    # Get the part before first non-latin1 character
                    pre_unicode = re.split(r'[^\x00-\xFF]', text)[0].strip().rstrip('(').strip()
                    if len(pre_unicode) > 5:
                        result = pre_unicode
                        if latin_parts:
                            result = result + " (" + latin_parts[0] + ")"
                    elif latin_parts:
                        result = latin_parts[0]
                    else:
                        result = re.sub(r'[^\x00-\xFF]', '', text).strip()
                    return result.strip() or "N/A"

                class PatientPDF(FPDF):
                    def header(self):
                        self.set_fill_color(0, 114, 255)
                        self.rect(0, 0, 210, 22, 'F')
                        self.set_text_color(255, 255, 255)
                        self.set_font("Helvetica", "B", 14)
                        self.set_xy(10, 5)
                        self.cell(0, 12, "CareFlow AI  |  Patient Medical Report", align="L")
                        self.set_font("Helvetica", "", 9)
                        self.set_xy(10, 13)
                        self.cell(0, 6, f"Generated: {pd.Timestamp.now().strftime('%d %B %Y, %H:%M')}  |  Confidential", align="L")
                        self.ln(18)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font("Helvetica", "I", 8)
                        self.set_text_color(150, 150, 150)
                        self.cell(0, 10, "CareFlow Medical Center  |  Page " + str(self.page_no()) + "  |  Confidential", align="C")

                    def section_title(self, title, r=0, g=114, b=255):
                        self.set_fill_color(r, g, b)
                        self.set_text_color(255, 255, 255)
                        self.set_font("Helvetica", "B", 11)
                        self.cell(0, 9, "  " + title, new_x="LMARGIN", new_y="NEXT", fill=True)
                        self.set_text_color(30, 30, 30)
                        self.ln(2)

                    def info_row(self, label, value, fill=False):
                        self.set_font("Helvetica", "B", 10)
                        self.set_fill_color(245, 247, 250)
                        self.set_text_color(80, 80, 80)
                        self.cell(60, 8, "  " + safe(label), fill=fill)
                        self.set_font("Helvetica", "", 10)
                        self.set_text_color(20, 20, 20)
                        self.cell(0, 8, safe(value), new_x="LMARGIN", new_y="NEXT", fill=fill)

                    def bullet_row(self, text, fill=False):
                        self.set_font("Helvetica", "", 9)
                        self.set_fill_color(245, 247, 250)
                        self.set_text_color(50, 50, 50)
                        clean = safe(text)[:95]
                        self.cell(0, 7, "  - " + clean, new_x="LMARGIN", new_y="NEXT", fill=fill)

                pdf = PatientPDF()
                pdf.set_auto_page_break(auto=True, margin=20)
                pdf.add_page()

                # PATIENT IDENTITY
                pdf.section_title("PATIENT IDENTITY", 30, 64, 175)
                pdf.info_row("Patient ID", patient.get("PatientID", "N/A"), fill=True)
                pdf.info_row("Full Name", patient.get("Name", "N/A"))
                pdf.info_row("Age", str(patient.get("Age", "N/A")) + " years", fill=True)
                pdf.info_row("Gender", patient.get("Gender", "N/A"))
                pdf.info_row("Blood Type", patient.get("BloodType", "N/A"), fill=True)
                pdf.ln(4)

                # ADMISSION DETAILS
                pdf.section_title("ADMISSION DETAILS", 0, 150, 136)
                adm_date = patient.get("DateofAdmission", "")
                dis_date = patient.get("DischargeDate", "")
                try:
                    adm_str = pd.Timestamp(adm_date).strftime("%d %B %Y") if adm_date else "N/A"
                except: adm_str = str(adm_date)
                try:
                    dis_str = pd.Timestamp(dis_date).strftime("%d %B %Y") if dis_date else "N/A"
                except: dis_str = str(dis_date)
                pdf.info_row("Admission Date", adm_str, fill=True)
                pdf.info_row("Discharge Date", dis_str)
                pdf.info_row("Length of Stay", str(patient.get("LengthOfStay", "N/A")) + " days", fill=True)
                pdf.info_row("Admission Type", patient.get("AdmissionType", "N/A"))
                pdf.info_row("Room Number", str(patient.get("RoomNumber", "N/A")), fill=True)
                pdf.info_row("Hospital", patient.get("Hospital", "CareFlow Medical Center"))
                pdf.ln(4)

                # MEDICAL INFORMATION
                pdf.section_title("MEDICAL INFORMATION", 220, 38, 38)
                pdf.info_row("Medical Condition", patient.get("MedicalCondition", "N/A"), fill=True)
                pdf.info_row("Medication", patient.get("Medication", "As prescribed"))
                pdf.info_row("Test Results", patient.get("TestResults", "Pending review"), fill=True)
                pdf.info_row("Attending Doctor", "Dr. " + safe(patient.get("Doctor", "N/A")))
                pdf.ln(4)

                # AI RISK ASSESSMENT
                risk_colors = {
                    "Critical": (239, 68, 68),
                    "High": (245, 158, 11),
                    "Medium": (234, 179, 8),
                    "Low": (16, 185, 129)
                }
                rc = risk_colors.get(risk_level, (100, 100, 100))
                pdf.section_title("AI RISK ASSESSMENT", rc[0], rc[1], rc[2])
                pdf.info_row("Risk Level", risk_level, fill=True)
                pdf.info_row("Risk Score", str(risk_score) + " / 100")
                # Risk bar
                y_bar = pdf.get_y() + 2
                pdf.set_fill_color(220, 220, 220)
                pdf.rect(10, y_bar, 190, 8, 'F')
                bar_w = max(4, int(190 * risk_score / 100))
                pdf.set_fill_color(*rc)
                pdf.rect(10, y_bar, bar_w, 8, 'F')
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(255, 255, 255)
                pdf.set_xy(13, y_bar + 1)
                pdf.cell(bar_w - 4, 6, str(risk_score) + "%")
                pdf.set_text_color(30, 30, 30)
                pdf.ln(14)

                # INSURANCE & BILLING
                pdf.section_title("INSURANCE & BILLING", 79, 70, 229)
                pdf.info_row("Insurance Provider", patient.get("InsuranceProvider", "N/A"), fill=True)
                billing = patient.get("BillingAmount", 0)
                try:
                    billing_fmt = "${:,.2f}".format(float(billing))
                except:
                    billing_fmt = str(billing)
                pdf.info_row("Total Billing Amount", billing_fmt)
                pdf.ln(4)

                # DISEASE INFORMATION
                from disease_info import get_disease_info
                disease_data = get_disease_info(patient.get("MedicalCondition", ""))
                if disease_data:
                    pdf.section_title("DISEASE INFORMATION & CARE PLAN", 102, 126, 234)

                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(60, 60, 60)
                    pdf.cell(0, 8, "  Key Symptoms:", new_x="LMARGIN", new_y="NEXT")
                    for i, sym in enumerate(disease_data["symptoms"][:5]):
                        pdf.bullet_row(sym, fill=(i % 2 == 0))
                    pdf.ln(2)

                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 8, "  Management & Treatment:", new_x="LMARGIN", new_y="NEXT")
                    for i, mgmt in enumerate(disease_data["management"][:5]):
                        pdf.bullet_row(mgmt, fill=(i % 2 == 0))
                    pdf.ln(2)

                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 8, "  Lifestyle Recommendations:", new_x="LMARGIN", new_y="NEXT")
                    for i, life in enumerate(disease_data["lifestyle"][:5]):
                        pdf.bullet_row(life, fill=(i % 2 == 0))
                    pdf.ln(4)

                # CLINICAL NOTES
                pdf.section_title("CLINICAL NOTES", 100, 100, 100)
                notes = patient.get("Notes", "")
                if not notes or str(notes).strip() in ["", "nan", "None"]:
                    notes = "No additional clinical notes recorded."
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(50, 50, 50)
                pdf.set_fill_color(250, 250, 250)
                pdf.multi_cell(0, 7, "  " + safe(notes), fill=True)
                pdf.ln(4)

                # DISCLAIMER
                pdf.set_fill_color(255, 243, 205)
                pdf.set_text_color(133, 100, 4)
                pdf.set_font("Helvetica", "I", 8)
                pdf.multi_cell(0, 6,
                    "  DISCLAIMER: This report is generated by CareFlow AI for authorized medical personnel only. "
                    "It is not a substitute for professional medical advice. All information is confidential "
                    "and protected under applicable healthcare privacy laws.",
                    fill=True
                )

                return bytes(pdf.output())

            # Generate and offer download
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_patient_pdf(p.to_dict(), risk_score, risk_level)

            st.success(f"✅ PDF ready for **{p['Name']}** ({p['MedicalCondition']})")

            st.download_button(
                label=f"⬇️ Download Full Patient Report — {p['Name']}.pdf",
                data=pdf_bytes,
                file_name=f"Patient_Report_{p['PatientID']}_{p['Name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # =========================================================
    # FEATURE 1 — ADD NEW RECORD FORM
    # =========================================================
    if st.session_state.show_add_form:
        st.markdown("---")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px 30px; border-radius: 14px; color: white; margin-bottom: 20px;">
                <h3 style="margin:0;">➕ Add New Patient Record</h3>
                <p style="margin:6px 0 0 0; opacity:0.85;">Fill in the details below to register a new patient</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("add_new_record_form", clear_on_submit=False):
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                new_name = st.text_input("👤 Full Name *", placeholder="e.g. Rahul Sharma")
            with r1c2:
                new_age = st.number_input("🎂 Age *", min_value=0, max_value=120, value=30)
            with r1c3:
                new_gender = st.selectbox("⚧ Gender *", ["Male", "Female", "Other"])

            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1:
                new_blood = st.selectbox("🩸 Blood Type",
                    sorted(df["BloodType"].dropna().unique().tolist()))
            with r2c2:
                new_condition = st.selectbox("🏥 Medical Condition *",
                    sorted(df["MedicalCondition"].dropna().unique().tolist()))
            with r2c3:
                new_admission_type = st.selectbox("🚑 Admission Type",
                    sorted(df["AdmissionType"].dropna().unique().tolist()))

            r3c1, r3c2, r3c3 = st.columns(3)
            with r3c1:
                new_doctor = st.selectbox("👨‍⚕️ Assigned Doctor",
                    sorted(df["Doctor"].dropna().unique().tolist()))
            with r3c2:
                new_room = st.number_input("🛏️ Room Number", min_value=1, max_value=999, value=101)
            with r3c3:
                new_insurance = st.selectbox("🛡️ Insurance Provider",
                    sorted(df["InsuranceProvider"].dropna().unique().tolist()))

            r4c1, r4c2, r4c3 = st.columns(3)
            with r4c1:
                new_admission_date = st.date_input("📅 Admission Date",
                    value=pd.Timestamp.today().date())
            with r4c2:
                new_discharge_date = st.date_input("📅 Discharge Date",
                    value=(pd.Timestamp.today() + pd.Timedelta(days=5)).date())
            with r4c3:
                new_billing = st.number_input("💰 Billing Amount ($)", min_value=0.0, value=5000.0, step=100.0)

            new_medication = st.text_input("💊 Medication", placeholder="e.g. Metformin 500mg")
            new_test_results = st.selectbox("🔬 Test Results", ["Normal", "Abnormal", "Inconclusive", "Pending"])
            new_hospital = st.selectbox("🏥 Hospital",
                sorted(df["Hospital"].dropna().unique().tolist()))
            new_notes = st.text_area("📝 Clinical Notes", placeholder="Enter any additional notes or observations...")

            submitted = st.form_submit_button("✅ Save Patient Record", use_container_width=True)

        # Handle submission OUTSIDE the form to avoid rerun conflicts
        if submitted:
            if not new_name.strip():
                st.error("❌ Patient name is required.")
            elif new_discharge_date < new_admission_date:
                st.error("❌ Discharge date cannot be before admission date.")
            else:
                new_id = f"PAT{len(df) + len(st.session_state.new_records) + 1:04d}"
                new_record = {
                    "PatientID": new_id,
                    "Name": new_name.strip(),
                    "Age": int(new_age),
                    "Gender": new_gender,
                    "BloodType": new_blood,
                    "MedicalCondition": new_condition,
                    "AdmissionType": new_admission_type,
                    "Doctor": new_doctor,
                    "RoomNumber": int(new_room),
                    "InsuranceProvider": new_insurance,
                    "Hospital": new_hospital,
                    "DateofAdmission": pd.Timestamp(new_admission_date),
                    "DischargeDate": pd.Timestamp(new_discharge_date),
                    "BillingAmount": float(new_billing),
                    "Medication": new_medication,
                    "TestResults": new_test_results,
                    "Notes": new_notes,
                    "LengthOfStay": (new_discharge_date - new_admission_date).days,
                    "AddedBy": st.session_state["name"],
                    "AddedAt": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.new_records.append(new_record)
                st.session_state.show_add_form = False
                st.session_state["last_added_patient"] = new_name.strip()
                st.session_state["last_added_id"] = new_id
                st.rerun()

    # Show success message after rerun
    if st.session_state.get("last_added_patient"):
        st.success(f"✅ Patient **{st.session_state['last_added_patient']}** added successfully! ID: **{st.session_state['last_added_id']}**")
        st.balloons()
        # Clear the flag so it doesn't show again on next rerun
        del st.session_state["last_added_patient"]
        del st.session_state["last_added_id"]

    # Show newly added records summary
    if st.session_state.new_records:
        with st.expander(f"🆕 Newly Added Records This Session ({len(st.session_state.new_records)})", expanded=False):
            new_df_display = pd.DataFrame(st.session_state.new_records)
            st.dataframe(
                new_df_display[["PatientID", "Name", "Age", "Gender", "MedicalCondition", "Doctor", "DateofAdmission"]],
                use_container_width=True
            )
            if st.button("🗑️ Clear Session Records", key="clear_new_records"):
                st.session_state.new_records = []
                st.rerun()

    # =========================================================
    # FEATURE 5 — INVOICE / BILL GENERATOR
    # =========================================================
    if st.session_state.get("show_invoice", False):
        st.markdown("---")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                        padding: 20px 30px; border-radius: 14px; color: white; margin-bottom: 20px;">
                <h3 style="margin:0;">🧾 Patient Invoice Generator</h3>
                <p style="margin:6px 0 0 0; opacity:0.85;">Generate detailed billing invoice for any patient</p>
            </div>
        """, unsafe_allow_html=True)

        # Patient selector
        inv_col1, inv_col2 = st.columns([2, 1])
        with inv_col1:
            patient_options_inv = [f"{row['PatientID']} — {row['Name']} ({row['MedicalCondition']})"
                                   for _, row in filtered_df.head(100).iterrows()]
            selected_inv_patient = st.selectbox("👤 Select Patient for Invoice", patient_options_inv, key="inv_patient_select")
        with inv_col2:
            invoice_date = st.date_input("📅 Invoice Date", value=pd.Timestamp.today().date(), key="inv_date")

        if selected_inv_patient:
            pid = selected_inv_patient.split(" — ")[0]
            patient_row = filtered_df[filtered_df["PatientID"] == pid].iloc[0]

            # Calculate itemized charges
            base_room = patient_row.get("LengthOfStay", 5) * 2500
            doctor_fee = np.random.randint(3000, 8000)
            lab_tests = np.random.randint(1500, 5000)
            medication_cost = np.random.randint(2000, 8000)
            nursing_charges = patient_row.get("LengthOfStay", 5) * 800
            misc_charges = np.random.randint(500, 2000)
            subtotal = base_room + doctor_fee + lab_tests + medication_cost + nursing_charges + misc_charges
            
            # Insurance deduction
            insurance_pct = 0.70 if patient_row.get("InsuranceProvider", "") != "" else 0.0
            insurance_deduction = subtotal * insurance_pct
            gst = (subtotal - insurance_deduction) * 0.05
            total_payable = subtotal - insurance_deduction + gst

            # Invoice display
            ins_pct_display = int(insurance_pct * 100)
            inv_html = f"""
<div style="background:white;border:2px solid #e5e7eb;border-radius:16px;padding:30px;margin:20px 0;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

  <div style="display:flex;justify-content:space-between;align-items:start;border-bottom:2px solid #e5e7eb;padding-bottom:20px;margin-bottom:20px;">
    <div>
      <h2 style="margin:0;color:#1f2937;">CareFlow Medical Center</h2>
      <p style="margin:4px 0;color:#6b7280;">123 Healthcare Avenue, Medical District</p>
      <p style="margin:4px 0;color:#6b7280;">Phone: +91-11-4567-8900 | GST: 07AABCC1234D1Z5</p>
    </div>
    <div style="text-align:right;">
      <h3 style="margin:0;color:#10b981;">INVOICE</h3>
      <p style="margin:4px 0;color:#6b7280;">Invoice #: INV-{pid}-{invoice_date.strftime('%Y%m%d')}</p>
      <p style="margin:4px 0;color:#6b7280;">Date: {invoice_date.strftime('%d %B %Y')}</p>
    </div>
  </div>

  <div style="display:flex;gap:30px;background:#f9fafb;padding:16px;border-radius:10px;margin-bottom:20px;flex-wrap:wrap;">
    <div><p style="margin:0;color:#6b7280;font-size:0.8rem;">PATIENT NAME</p><p style="margin:4px 0;color:#1f2937;font-weight:600;">{patient_row['Name']}</p></div>
    <div><p style="margin:0;color:#6b7280;font-size:0.8rem;">PATIENT ID</p><p style="margin:4px 0;color:#1f2937;font-weight:600;">{pid}</p></div>
    <div><p style="margin:0;color:#6b7280;font-size:0.8rem;">CONDITION</p><p style="margin:4px 0;color:#1f2937;font-weight:600;">{patient_row['MedicalCondition']}</p></div>
    <div><p style="margin:0;color:#6b7280;font-size:0.8rem;">DOCTOR</p><p style="margin:4px 0;color:#1f2937;font-weight:600;">Dr. {patient_row['Doctor']}</p></div>
    <div><p style="margin:0;color:#6b7280;font-size:0.8rem;">INSURANCE</p><p style="margin:4px 0;color:#1f2937;font-weight:600;">{patient_row.get('InsuranceProvider', 'N/A')}</p></div>
  </div>

  <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
    <thead>
      <tr style="background:#1f2937;color:white;">
        <th style="padding:12px 16px;text-align:left;">Description</th>
        <th style="padding:12px 16px;text-align:center;">Qty/Days</th>
        <th style="padding:12px 16px;text-align:right;">Rate</th>
        <th style="padding:12px 16px;text-align:right;">Amount</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom:1px solid #e5e7eb;">
        <td style="padding:12px 16px;color:#374151;">Room &amp; Board Charges</td>
        <td style="padding:12px 16px;text-align:center;">{patient_row.get('LengthOfStay', 5)} days</td>
        <td style="padding:12px 16px;text-align:right;">Rs.2,500/day</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{base_room:,.0f}</td>
      </tr>
      <tr style="border-bottom:1px solid #e5e7eb;background:#f9fafb;">
        <td style="padding:12px 16px;color:#374151;">Doctor Consultation Fee</td>
        <td style="padding:12px 16px;text-align:center;">1</td>
        <td style="padding:12px 16px;text-align:right;">Rs.{doctor_fee:,.0f}</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{doctor_fee:,.0f}</td>
      </tr>
      <tr style="border-bottom:1px solid #e5e7eb;">
        <td style="padding:12px 16px;color:#374151;">Laboratory &amp; Diagnostic Tests</td>
        <td style="padding:12px 16px;text-align:center;">1</td>
        <td style="padding:12px 16px;text-align:right;">Rs.{lab_tests:,.0f}</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{lab_tests:,.0f}</td>
      </tr>
      <tr style="border-bottom:1px solid #e5e7eb;background:#f9fafb;">
        <td style="padding:12px 16px;color:#374151;">Medications &amp; Pharmacy</td>
        <td style="padding:12px 16px;text-align:center;">1</td>
        <td style="padding:12px 16px;text-align:right;">Rs.{medication_cost:,.0f}</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{medication_cost:,.0f}</td>
      </tr>
      <tr style="border-bottom:1px solid #e5e7eb;">
        <td style="padding:12px 16px;color:#374151;">Nursing &amp; Care Charges</td>
        <td style="padding:12px 16px;text-align:center;">{patient_row.get('LengthOfStay', 5)} days</td>
        <td style="padding:12px 16px;text-align:right;">Rs.800/day</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{nursing_charges:,.0f}</td>
      </tr>
      <tr style="border-bottom:2px solid #e5e7eb;background:#f9fafb;">
        <td style="padding:12px 16px;color:#374151;">Miscellaneous Charges</td>
        <td style="padding:12px 16px;text-align:center;">1</td>
        <td style="padding:12px 16px;text-align:right;">Rs.{misc_charges:,.0f}</td>
        <td style="padding:12px 16px;text-align:right;font-weight:600;">Rs.{misc_charges:,.0f}</td>
      </tr>
    </tbody>
  </table>

  <div style="display:flex;justify-content:flex-end;">
    <div style="min-width:320px;">
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #e5e7eb;">
        <span style="color:#6b7280;">Subtotal</span>
        <span style="font-weight:600;color:#1f2937;">Rs.{subtotal:,.0f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #e5e7eb;color:#10b981;">
        <span>Insurance Coverage ({ins_pct_display}%)</span>
        <span style="font-weight:600;">- Rs.{insurance_deduction:,.0f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #e5e7eb;">
        <span style="color:#6b7280;">GST (5%)</span>
        <span style="font-weight:600;color:#1f2937;">Rs.{gst:,.0f}</span>
      </div>
      <div style="display:flex;justify-content:space-between;background:#1f2937;border-radius:8px;padding:12px 16px;margin-top:8px;">
        <span style="color:white;font-size:1.1rem;font-weight:700;">TOTAL PAYABLE</span>
        <span style="color:#38ef7d;font-size:1.2rem;font-weight:700;">Rs.{total_payable:,.0f}</span>
      </div>
    </div>
  </div>

  <div style="margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;text-align:center;color:#9ca3af;font-size:0.85rem;">
    Thank you for choosing CareFlow Medical Center. Billing queries: billing@careflow.in | +91-11-4567-8901
  </div>
</div>
"""
            st.markdown(inv_html, unsafe_allow_html=True)

            # Download invoice as CSV
            invoice_data = {
                "Item": ["Room & Board", "Doctor Fee", "Lab Tests", "Medications", "Nursing", "Misc", "Subtotal", f"Insurance ({insurance_pct*100:.0f}%)", "GST (5%)", "TOTAL PAYABLE"],
                "Amount (₹)": [base_room, doctor_fee, lab_tests, medication_cost, nursing_charges, misc_charges, subtotal, -insurance_deduction, gst, total_payable]
            }
            inv_csv = pd.DataFrame(invoice_data).to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"⬇️ Download Invoice for {patient_row['Name']} (CSV)",
                data=inv_csv,
                file_name=f"invoice_{pid}_{invoice_date.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # =========================================================
    # FEATURE 2 — GENERATE REPORT
    # =========================================================
    if st.session_state.show_report:
        st.markdown("---")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        padding: 20px 30px; border-radius: 14px; color: white; margin-bottom: 20px;">
                <h3 style="margin:0;">📊 Patient Records Report</h3>
                <p style="margin:6px 0 0 0; opacity:0.85;">Auto-generated summary based on current filtered records</p>
            </div>
        """, unsafe_allow_html=True)

        report_df = filtered_df.copy()
        generated_at = pd.Timestamp.now().strftime("%d %B %Y, %H:%M")

        # --- Summary KPIs ---
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Patients", f"{len(report_df):,}")
        k2.metric("Avg Age", f"{report_df['Age'].mean():.1f} yrs")
        k3.metric("Avg Billing", f"${report_df['BillingAmount'].mean():,.0f}")
        avg_stay = report_df["LengthOfStay"].mean() if "LengthOfStay" in report_df.columns else 0
        k4.metric("Avg Stay", f"{avg_stay:.1f} days")
        k5.metric("Unique Doctors", f"{report_df['Doctor'].nunique()}")

        st.markdown(f"<p style='color:#888; font-size:0.85rem;'>Report generated by <b>{st.session_state['name']}</b> on {generated_at}</p>", unsafe_allow_html=True)
        st.markdown("---")

        # --- Charts Row 1 ---
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("#### 🏥 Patients by Medical Condition")
            cond_counts = report_df["MedicalCondition"].value_counts().reset_index()
            cond_counts.columns = ["Condition", "Count"]
            fig_cond = px.bar(cond_counts, x="Count", y="Condition", orientation="h",
                              color="Count", color_continuous_scale="Purples")
            fig_cond.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig_cond, use_container_width=True)

        with rc2:
            st.markdown("#### ⚧ Gender Distribution")
            gender_counts = report_df["Gender"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            fig_gender = px.pie(gender_counts, names="Gender", values="Count",
                                color_discrete_sequence=["#f093fb", "#4facfe", "#38ef7d"])
            fig_gender.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_gender, use_container_width=True)

        # --- Charts Row 2 ---
        rc3, rc4 = st.columns(2)
        with rc3:
            st.markdown("#### 🚑 Admission Type Breakdown")
            adm_counts = report_df["AdmissionType"].value_counts().reset_index()
            adm_counts.columns = ["Type", "Count"]
            fig_adm = px.pie(adm_counts, names="Type", values="Count", hole=0.5,
                             color_discrete_sequence=["#f6d365", "#fda085", "#f5576c"])
            fig_adm.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_adm, use_container_width=True)

        with rc4:
            st.markdown("#### 💰 Billing Amount by Condition")
            billing_avg = report_df.groupby("MedicalCondition")["BillingAmount"].mean().reset_index()
            billing_avg.columns = ["Condition", "Avg Billing"]
            fig_bill = px.bar(billing_avg, x="Condition", y="Avg Billing",
                              color="Avg Billing", color_continuous_scale="Reds")
            fig_bill.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                   xaxis_tickangle=-30, showlegend=False)
            st.plotly_chart(fig_bill, use_container_width=True)

        # --- Charts Row 3 ---
        rc5, rc6 = st.columns(2)
        with rc5:
            st.markdown("#### 🛡️ Insurance Provider Share")
            ins_counts = report_df["InsuranceProvider"].value_counts().reset_index()
            ins_counts.columns = ["Provider", "Count"]
            fig_ins = px.bar(ins_counts, x="Provider", y="Count",
                             color="Count", color_continuous_scale="Blues")
            fig_ins.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                  xaxis_tickangle=-30, showlegend=False)
            st.plotly_chart(fig_ins, use_container_width=True)

        with rc6:
            st.markdown("#### 📅 Admissions Over Time")
            if "DateofAdmission" in report_df.columns:
                timeline = report_df.copy()
                timeline["Month"] = pd.to_datetime(timeline["DateofAdmission"]).dt.to_period("M").astype(str)
                monthly = timeline.groupby("Month").size().reset_index(name="Admissions")
                monthly = monthly.tail(12)
                fig_time = px.line(monthly, x="Month", y="Admissions",
                                   markers=True, color_discrete_sequence=["#f5576c"])
                fig_time.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                       xaxis_tickangle=-30)
                st.plotly_chart(fig_time, use_container_width=True)

        # --- Top Doctors Table ---
        st.markdown("#### 👨‍⚕️ Top Doctors by Patient Load")
        top_docs = report_df.groupby("Doctor").agg(
            Patients=("Name", "count"),
            Avg_Billing=("BillingAmount", "mean"),
            Conditions=("MedicalCondition", lambda x: ", ".join(x.unique()[:3]))
        ).reset_index().sort_values("Patients", ascending=False).head(10)
        top_docs["Avg_Billing"] = top_docs["Avg_Billing"].map("${:,.0f}".format)
        st.dataframe(top_docs, use_container_width=True)

        # --- Condition Summary Table ---
        st.markdown("#### 📋 Condition-wise Summary")
        cond_summary = report_df.groupby("MedicalCondition").agg(
            Total_Patients=("Name", "count"),
            Avg_Age=("Age", "mean"),
            Avg_Billing=("BillingAmount", "mean"),
            Male=("Gender", lambda x: (x == "Male").sum()),
            Female=("Gender", lambda x: (x == "Female").sum())
        ).reset_index()
        cond_summary["Avg_Age"] = cond_summary["Avg_Age"].map("{:.1f}".format)
        cond_summary["Avg_Billing"] = cond_summary["Avg_Billing"].map("${:,.0f}".format)
        st.dataframe(cond_summary, use_container_width=True)

        # --- Download Report as CSV ---
        st.markdown("#### ⬇️ Download Full Report")
        dc1, dc2 = st.columns(2)
        with dc1:
            csv_report = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Patient Data (CSV)",
                data=csv_report,
                file_name=f"healthcare_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dc2:
            summary_csv = cond_summary.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Condition Summary (CSV)",
                data=summary_csv,
                file_name=f"condition_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# --- PAGE 5: APPOINTMENTS ---
elif page == "📅 Appointments":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">📅 Appointment Scheduler</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Manage patient appointments and schedules</p>
        </div>
    """, unsafe_allow_html=True)

    # Appointment Calendar View
    col_cal, col_list = st.columns([2, 1])

    with col_cal:
        st.markdown("### 📆 Calendar View")
        # Mock calendar - in real app this would be a proper calendar component
        calendar_dates = pd.date_range(start=pd.Timestamp.today(), periods=7, freq='D')

        for date in calendar_dates:
            date_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A')
            day_num = date.strftime('%d')

            # Count appointments for this date (mock data)
            apt_count = np.random.randint(0, 8)

            st.markdown(f"""
                <div style="background: {'#e3f2fd' if apt_count > 5 else '#f3e5f5' if apt_count > 2 else '#e8f5e8'}; 
                           padding: 15px; margin: 5px 0; border-radius: 8px; border-left: 4px solid {'#2196f3' if apt_count > 5 else '#9c27b0' if apt_count > 2 else '#4caf50'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{day_name}</strong><br>
                            <span style="color: #666;">{day_num}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5rem; font-weight: bold;">{apt_count}</div>
                            <div style="font-size: 0.8rem; color: #666;">appointments</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_list:
        st.markdown("### 📋 Today's Schedule")
        # Mock today's appointments
        today_appts = [
            {"time": "09:00", "patient": "John Smith", "type": "Follow-up", "status": "confirmed"},
            {"time": "10:30", "patient": "Sarah Johnson", "type": "Consultation", "status": "confirmed"},
            {"time": "14:00", "patient": "Mike Davis", "type": "Check-up", "status": "pending"},
            {"time": "15:30", "patient": "Emma Wilson", "type": "Results Review", "status": "confirmed"},
        ]

        for appt in today_appts:
            status_color = "#4caf50" if appt["status"] == "confirmed" else "#ff9800"
            st.markdown(f"""
                <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {status_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-weight: bold; color: #333;">{appt['time']} - {appt['patient']}</div>
                    <div style="font-size: 0.9rem; color: #666;">{appt['type']} • <span style="color: {status_color};">{appt['status']}</span></div>
                </div>
            """, unsafe_allow_html=True)

    # Initialize appointments in session state if not exists
    if 'appointments' not in st.session_state:
        st.session_state.appointments = []

    # Appointment Booking Form
    st.markdown("### 📅 Book New Appointment")
    with st.expander("➕ Schedule Appointment", expanded=False):
        with st.form("appointment_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Patient selection from existing patients
                patient_options = [f"{row['PatientID']} - {row['Name']} ({row['Age']}y, {row['MedicalCondition']})"
                                 for _, row in df_selection.iterrows()]
                selected_patient = st.selectbox("👤 Select Patient", patient_options)

                # Extract patient ID from selection
                patient_id = selected_patient.split(' - ')[0] if selected_patient else None

                # Doctor selection
                doctor_options = df_selection['Doctor'].unique().tolist()
                selected_doctor = st.selectbox("👨‍⚕️ Select Doctor", doctor_options)

                # Appointment type
                appointment_types = ["Consultation", "Follow-up", "Check-up", "Emergency", "Surgery", "Therapy", "Diagnostic", "Vaccination"]
                appointment_type = st.selectbox("📋 Appointment Type", appointment_types)

            with col2:
                # Date selection
                appointment_date = st.date_input("📅 Select Date",
                                               min_value=pd.Timestamp.today().date(),
                                               max_value=pd.Timestamp.today().date() + pd.Timedelta(days=90))

                # Time selection
                time_options = [f"{hour:02d}:{minute:02d}" for hour in range(8, 18)
                              for minute in [0, 15, 30, 45]]
                appointment_time = st.selectbox("⏰ Select Time", time_options)

                # Duration
                duration_options = ["15 minutes", "30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"]
                duration = st.selectbox("⏱️ Duration", duration_options)

            # Reason/Notes
            appointment_notes = st.text_area("📝 Reason/Notes", placeholder="Please describe the reason for this appointment...")

            # Submit button
            submitted = st.form_submit_button("📅 Book Appointment", use_container_width=True)

            if submitted:
                if not selected_patient or not selected_doctor:
                    st.error("Please select both patient and doctor.")
                else:
                    # Create appointment record
                    appointment = {
                        'id': f"APT{len(st.session_state.appointments) + 1:04d}",
                        'patient_id': patient_id,
                        'patient_name': selected_patient.split(' - ')[1].split(' (')[0],
                        'doctor': selected_doctor,
                        'date': appointment_date.strftime('%Y-%m-%d'),
                        'time': appointment_time,
                        'duration': duration,
                        'type': appointment_type,
                        'notes': appointment_notes,
                        'status': 'confirmed',
                        'booked_by': st.session_state['name'],
                        'booked_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    st.session_state.appointments.append(appointment)
                    st.success(f"✅ Appointment booked successfully! ID: {appointment['id']}")

                    # Show confirmation details
                    st.info(f"""
                    **Appointment Details:**
                    - **Patient:** {appointment['patient_name']}
                    - **Doctor:** {appointment['doctor']}
                    - **Date & Time:** {appointment['date']} at {appointment['time']}
                    - **Duration:** {appointment['duration']}
                    - **Type:** {appointment['type']}
                    """)

    # Display Booked Appointments
    st.markdown("### 📋 My Appointments")

    if st.session_state.appointments:
        # Filter appointments by current user (doctor or admin can see all, patients see their own)
        user_appointments = st.session_state.appointments

        if st.session_state['username'] != 'admin':
            # If not admin, show only appointments for this doctor or patient's appointments
            user_appointments = [apt for apt in user_appointments
                               if apt['doctor'] == st.session_state['name'] or
                                  apt['booked_by'] == st.session_state['name']]

        if user_appointments:
            # Sort by date and time
            user_appointments.sort(key=lambda x: f"{x['date']} {x['time']}")

            for apt in user_appointments:
                status_color = "#4caf50" if apt["status"] == "confirmed" else "#ff9800" if apt["status"] == "pending" else "#f44336"

                with st.container():
                    col_info, col_actions = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"""
                        <div style="background: white; padding: 15px; margin: 8px 0; border-radius: 10px; border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                <div>
                                    <h4 style="margin: 0; color: #1f2937;">{apt['patient_name']}</h4>
                                    <p style="margin: 5px 0; color: #6b7280; font-size: 0.9rem;">ID: {apt['id']} • Dr. {apt['doctor']}</p>
                                </div>
                                <span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">{apt['status'].upper()}</span>
                            </div>
                            <div style="display: flex; gap: 20px; margin-bottom: 10px;">
                                <div><strong>📅 Date:</strong> {apt['date']}</div>
                                <div><strong>⏰ Time:</strong> {apt['time']}</div>
                                <div><strong>⏱️ Duration:</strong> {apt['duration']}</div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <strong>📋 Type:</strong> {apt['type']}
                            </div>
                            """, unsafe_allow_html=True)

                        # Add notes if they exist
                        if apt['notes']:
                            st.markdown(f"""
                            <div style="margin-bottom: 10px;">
                                <strong>📝 Notes:</strong> {apt['notes']}
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style="font-size: 0.8rem; color: #666; margin-top: 10px;">
                                Booked by {apt['booked_by']} on {apt['booked_at']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_actions:
                        if apt['status'] == 'confirmed':
                            if st.button("❌ Cancel", key=f"cancel_{apt['id']}", help="Cancel this appointment"):
                                apt['status'] = 'cancelled'
                                st.rerun()
                        elif apt['status'] == 'pending':
                            col_confirm, col_reject = st.columns(2)
                            with col_confirm:
                                if st.button("✅ Confirm", key=f"confirm_{apt['id']}", help="Confirm this appointment"):
                                    apt['status'] = 'confirmed'
                                    st.rerun()
                            with col_reject:
                                if st.button("❌ Reject", key=f"reject_{apt['id']}", help="Reject this appointment"):
                                    apt['status'] = 'cancelled'
                                    st.rerun()
        else:
            st.info("No appointments found for your account.")
    else:
        st.info("No appointments booked yet. Use the form above to schedule your first appointment!")

    # Quick Statistics
    st.markdown("### 📊 Appointment Statistics")
    col1, col2, col3, col4 = st.columns(4)

    total_appts = len(st.session_state.appointments)
    confirmed_appts = len([apt for apt in st.session_state.appointments if apt['status'] == 'confirmed'])
    pending_appts = len([apt for apt in st.session_state.appointments if apt['status'] == 'pending'])
    today_appts = len([apt for apt in st.session_state.appointments
                      if apt['date'] == pd.Timestamp.today().strftime('%Y-%m-%d') and apt['status'] == 'confirmed'])

    with col1:
        st.metric("Total Appointments", total_appts)
    with col2:
        st.metric("Confirmed", confirmed_appts, "🟢" if confirmed_appts > 0 else "")
    with col3:
        st.metric("Pending", pending_appts, "🟡" if pending_appts > 0 else "")
    with col4:
        st.metric("Today", today_appts, "📅" if today_appts > 0 else "")

    # =========================================================
    # FEATURE 10 — APPOINTMENT REMINDER (WhatsApp / Email)
    # =========================================================
    st.markdown("---")
    st.markdown("""
        <div style="background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                    padding: 20px 30px; border-radius: 14px; color: white; margin-bottom: 20px;">
            <h3 style="margin:0;">📲 Send Appointment Reminders</h3>
            <p style="margin:6px 0 0 0; opacity:0.85;">Send WhatsApp or Email reminders to patients for upcoming appointments</p>
        </div>
    """, unsafe_allow_html=True)

    if "reminder_log" not in st.session_state:
        st.session_state.reminder_log = []

    rem_col1, rem_col2 = st.columns([1, 1])

    with rem_col1:
        st.markdown("#### 📤 Send Reminder")
        with st.form("reminder_form"):
            # Channel selection
            reminder_channel = st.radio("📡 Reminder Channel", ["📱 WhatsApp", "📧 Email", "📱 Both"], horizontal=True)

            # Patient info
            reminder_name = st.text_input("👤 Patient Name", placeholder="e.g. Rahul Sharma")
            
            if "📧" in reminder_channel or "Both" in reminder_channel:
                reminder_email = st.text_input("📧 Email Address", placeholder="patient@email.com")
            else:
                reminder_email = ""
            
            if "📱 WhatsApp" in reminder_channel or "Both" in reminder_channel:
                reminder_phone = st.text_input("📱 WhatsApp Number", placeholder="+91 98765 43210")
            else:
                reminder_phone = ""

            # Appointment details
            rem_date = st.date_input("📅 Appointment Date", min_value=pd.Timestamp.today().date())
            rem_time = st.selectbox("⏰ Appointment Time",
                [f"{h:02d}:{m:02d}" for h in range(8, 18) for m in [0, 30]])
            rem_doctor = st.selectbox("👨‍⚕️ Doctor", sorted(df["Doctor"].unique().tolist()))
            rem_type = st.selectbox("📋 Appointment Type",
                ["Consultation", "Follow-up", "Check-up", "Emergency", "Surgery", "Therapy"])

            # Custom message
            custom_msg = st.text_area("💬 Custom Message (optional)",
                placeholder="Add any special instructions or notes...")

            send_btn = st.form_submit_button("🚀 Send Reminder", use_container_width=True)

            if send_btn:
                if not reminder_name.strip():
                    st.error("❌ Patient name is required.")
                else:
                    # Build reminder message
                    msg_template = f"""
🏥 *CareFlow Medical Center*
━━━━━━━━━━━━━━━━━━━━
📋 *Appointment Reminder*

Dear *{reminder_name}*,

Your appointment has been scheduled:

📅 *Date:* {rem_date.strftime('%d %B %Y')}
⏰ *Time:* {rem_time}
👨‍⚕️ *Doctor:* Dr. {rem_doctor}
📋 *Type:* {rem_type}

📍 *Location:* CareFlow Medical Center
   123 Healthcare Avenue, Medical District

{f'📝 *Note:* {custom_msg}' if custom_msg else ''}

Please arrive 15 minutes early.
For queries: +91-11-4567-8900

_This is an automated reminder from CareFlow AI_
                    """.strip()

                    # Log the reminder
                    log_entry = {
                        "id": f"REM{len(st.session_state.reminder_log)+1:04d}",
                        "patient": reminder_name,
                        "channel": reminder_channel,
                        "phone": reminder_phone if reminder_phone else "—",
                        "email": reminder_email if reminder_email else "—",
                        "date": rem_date.strftime('%Y-%m-%d'),
                        "time": rem_time,
                        "doctor": rem_doctor,
                        "type": rem_type,
                        "sent_at": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "sent_by": st.session_state["name"],
                        "status": "✅ Sent"
                    }
                    st.session_state.reminder_log.append(log_entry)

                    st.success(f"✅ Reminder sent successfully to **{reminder_name}** via {reminder_channel}!")
                    st.balloons()

    with rem_col2:
        st.markdown("#### 📋 Reminder Preview")
        if st.session_state.reminder_log:
            last = st.session_state.reminder_log[-1]
            st.markdown(f"""
                <div style="background: #075E54; color: white; padding: 20px; border-radius: 16px; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
                    <div style="background: #128C7E; padding: 10px 14px; border-radius: 10px; margin-bottom: 12px;">
                        <strong>🏥 CareFlow Medical Center</strong><br>
                        ━━━━━━━━━━━━━━━━━━━━<br>
                        📋 <strong>Appointment Reminder</strong>
                    </div>
                    <div style="background: #1F2C34; padding: 14px; border-radius: 10px;">
                        Dear <strong>{last['patient']}</strong>,<br><br>
                        📅 <strong>Date:</strong> {pd.Timestamp(last['date']).strftime('%d %B %Y')}<br>
                        ⏰ <strong>Time:</strong> {last['time']}<br>
                        👨‍⚕️ <strong>Doctor:</strong> Dr. {last['doctor']}<br>
                        📋 <strong>Type:</strong> {last['type']}<br><br>
                        📍 CareFlow Medical Center<br>
                        123 Healthcare Avenue<br><br>
                        <em style="color: #aaa;">Please arrive 15 minutes early.</em>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.8rem; color: #aaa; text-align: right;">
                        Sent via {last['channel']} • {last['sent_at']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: #f3f4f6; padding: 40px; border-radius: 12px; text-align: center; color: #9ca3af;">
                    <p style="font-size: 2rem;">📲</p>
                    <p>Send a reminder to see the preview here</p>
                </div>
            """, unsafe_allow_html=True)

    # Reminder Log
    if st.session_state.reminder_log:
        st.markdown("#### 📜 Reminder History")
        log_df = pd.DataFrame(st.session_state.reminder_log)
        st.dataframe(
            log_df[["id", "patient", "channel", "phone", "email", "date", "time", "doctor", "sent_at", "status"]],
            use_container_width=True,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "patient": st.column_config.TextColumn("Patient", width="medium"),
                "channel": st.column_config.TextColumn("Channel", width="medium"),
                "date": st.column_config.TextColumn("Appt Date", width="small"),
                "time": st.column_config.TextColumn("Time", width="small"),
                "doctor": st.column_config.TextColumn("Doctor", width="medium"),
                "sent_at": st.column_config.TextColumn("Sent At", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Export reminder log
        rem_csv = log_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export Reminder Log (CSV)",
            data=rem_csv,
            file_name=f"reminder_log_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# --- PAGE 6: PRESCRIPTIONS ---
elif page == "💊 Prescriptions":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">💊 Prescription Management</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Digital prescription writing and medication tracking</p>
        </div>
    """, unsafe_allow_html=True)

    # Prescription Search and Filters
    col_search, col_status = st.columns([2, 1])
    with col_search:
        rx_search = st.text_input("🔍 Search Prescriptions", placeholder="Patient name, medication, or prescription ID...")
    with col_status:
        rx_status = st.selectbox("Status", ["All", "Active", "Completed", "Expired", "Discontinued"])

    # Mock prescription data
    prescriptions = [
        {"id": "RX001", "patient": "John Smith", "medication": "Lisinopril 10mg", "dosage": "1 tablet daily", "status": "Active", "prescribed": "2024-01-15", "expires": "2024-04-15"},
        {"id": "RX002", "patient": "Sarah Johnson", "medication": "Metformin 500mg", "dosage": "2 tablets twice daily", "status": "Active", "prescribed": "2024-01-10", "expires": "2024-04-10"},
        {"id": "RX003", "patient": "Mike Davis", "medication": "Amoxicillin 500mg", "dosage": "1 capsule every 8 hours", "status": "Completed", "prescribed": "2024-01-05", "expires": "2024-01-12"},
        {"id": "RX004", "patient": "Emma Wilson", "medication": "Omeprazole 20mg", "dosage": "1 capsule daily", "status": "Active", "prescribed": "2024-01-08", "expires": "2024-04-08"},
    ]

    # Display prescriptions
    st.markdown("### 📝 Active Prescriptions")
    for rx in prescriptions:
        if rx_status == "All" or rx["status"].lower() == rx_status.lower():
            status_color = {
                "Active": "#4caf50",
                "Completed": "#2196f3",
                "Expired": "#f44336",
                "Discontinued": "#9e9e9e"
            }.get(rx["status"], "#666")

            st.markdown(f"""
                <div style="background: white; padding: 20px; margin: 10px 0; border-radius: 12px; border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: #1f2937;">{rx['medication']}</h4>
                            <p style="margin: 5px 0; color: #6b7280;">Patient: {rx['patient']} • ID: {rx['id']}</p>
                            <p style="margin: 5px 0; color: #374151;"><strong>Dosage:</strong> {rx['dosage']}</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">{rx['status']}</span>
                            <p style="margin: 8px 0 0 0; font-size: 0.9rem; color: #666;">Expires: {rx['expires']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Prescription Analytics Dashboard
    st.markdown("### 📊 Prescription Analytics")

    # Analytics Tabs
    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["📈 Overview", "💊 Medication Trends", "👨‍⚕️ Doctor Insights"])

    with analytics_tab1:
        # Key Metrics
        st.markdown("#### 📊 Key Performance Indicators")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_rx = len(prescriptions)
            st.metric("Total Prescriptions", f"{total_rx:,}", "📋")
        with col2:
            active_rx = len([rx for rx in prescriptions if rx['status'] == 'Active'])
            st.metric("Active Prescriptions", f"{active_rx:,}", "🟢")
        with col3:
            # Mock cost calculation
            avg_cost = 127.50
            st.metric("Avg Monthly Cost", f"${avg_cost:.2f}", "💰")
        with col4:
            refill_rate = 78.5
            st.metric("Refill Compliance", f"{refill_rate}%", "📈")

        # Status Distribution
        st.markdown("#### 📊 Prescription Status Distribution")
        status_counts = {}
        for rx in prescriptions:
            status = rx['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
        fig_status = px.pie(status_df, values='Count', names='Status',
                           title='Prescription Status Distribution',
                           color_discrete_sequence=['#4caf50', '#2196f3', '#f44336', '#9e9e9e'])
        st.plotly_chart(fig_status, use_container_width=True)

    with analytics_tab2:
        st.markdown("#### 💊 Medication Usage Trends")

        # Extract medication data
        med_data = []
        for rx in prescriptions:
            med_name = rx['medication'].split(' ')[0]  # Get base medication name
            med_data.append({
                'medication': med_name,
                'status': rx['status'],
                'prescribed_date': pd.to_datetime(rx['prescribed'])
            })

        med_df = pd.DataFrame(med_data)

        # Popular Medications
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🏆 Top Prescribed Medications")
            med_counts = med_df['medication'].value_counts().head(5)
            fig_top_meds = px.bar(med_counts,
                                title='Most Prescribed Medications',
                                labels={'index': 'Medication', 'value': 'Prescriptions'},
                                color_discrete_sequence=['#4facfe'])
            fig_top_meds.update_layout(showlegend=False)
            st.plotly_chart(fig_top_meds, use_container_width=True)

        with col2:
            st.markdown("##### 📅 Monthly Prescription Trends")
            # Mock monthly data
            monthly_data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Prescriptions': [45, 52, 48, 61, 55, 49]
            })
            fig_monthly = px.line(monthly_data, x='Month', y='Prescriptions',
                                title='Monthly Prescription Volume',
                                markers=True, color_discrete_sequence=['#00f2fe'])
            st.plotly_chart(fig_monthly, use_container_width=True)

        # Medication Categories
        st.markdown("##### 🏥 Medication Categories")
        categories = {
            'Cardiovascular': ['Lisinopril', 'Amlodipine', 'Metoprolol'],
            'Diabetes': ['Metformin', 'Insulin', 'Glipizide'],
            'Antibiotics': ['Amoxicillin', 'Azithromycin', 'Ciprofloxacin'],
            'Gastrointestinal': ['Omeprazole', 'Pantoprazole', 'Ranitidine'],
            'Analgesics': ['Ibuprofen', 'Acetaminophen', 'Naproxen']
        }

        category_counts = {}
        for rx in prescriptions:
            med_name = rx['medication'].split(' ')[0]
            for category, meds in categories.items():
                if med_name in meds:
                    category_counts[category] = category_counts.get(category, 0) + 1
                    break
            else:
                category_counts['Other'] = category_counts.get('Other', 0) + 1

        category_df = pd.DataFrame(list(category_counts.items()), columns=['Category', 'Count'])
        fig_categories = px.bar(category_df, x='Category', y='Count',
                              title='Prescriptions by Category',
                              color='Category',
                              color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_categories, use_container_width=True)

    with analytics_tab3:
        st.markdown("#### 👨‍⚕️ Doctor Prescribing Insights")

        # Mock doctor data
        doctor_stats = [
            {"doctor": "Dr. Smith", "prescriptions": 45, "avg_cost": 156.78, "specialty": "Cardiology"},
            {"doctor": "Dr. Johnson", "prescriptions": 38, "avg_cost": 98.45, "specialty": "Internal Medicine"},
            {"doctor": "Dr. Davis", "prescriptions": 52, "avg_cost": 134.23, "specialty": "Family Medicine"},
            {"doctor": "Dr. Wilson", "prescriptions": 29, "avg_cost": 187.90, "specialty": "Endocrinology"},
            {"doctor": "Dr. Brown", "prescriptions": 41, "avg_cost": 112.67, "specialty": "Pediatrics"}
        ]

        doctor_df = pd.DataFrame(doctor_stats)

        # Doctor Performance Metrics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📋 Prescriptions by Doctor")
            fig_doctor_rx = px.bar(doctor_df, x='doctor', y='prescriptions',
                                 title='Prescription Volume by Doctor',
                                 color='specialty',
                                 labels={'doctor': 'Doctor', 'prescriptions': 'Prescriptions'})
            st.plotly_chart(fig_doctor_rx, use_container_width=True)

        with col2:
            st.markdown("##### 💰 Average Prescription Cost by Doctor")
            fig_doctor_cost = px.bar(doctor_df, x='doctor', y='avg_cost',
                                   title='Average Cost per Prescription',
                                   color='specialty',
                                   labels={'doctor': 'Doctor', 'avg_cost': 'Avg Cost ($)'})
            st.plotly_chart(fig_doctor_cost, use_container_width=True)

        # Doctor Specialty Analysis
        st.markdown("##### 🏥 Specialty-wise Analysis")
        specialty_summary = doctor_df.groupby('specialty').agg({
            'prescriptions': 'sum',
            'avg_cost': 'mean'
        }).reset_index()

        fig_specialty = px.scatter(specialty_summary, x='prescriptions', y='avg_cost',
                                 size='prescriptions', color='specialty',
                                 title='Specialty Performance Matrix',
                                 labels={'prescriptions': 'Total Prescriptions', 'avg_cost': 'Avg Cost ($)'},
                                 size_max=50)
        st.plotly_chart(fig_specialty, use_container_width=True)

    # Helper method for calculating readiness time
    def _calculate_readiness_time(urgency):
        now = pd.Timestamp.now()
        if "hour" in urgency.lower():
            return (now + pd.Timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        elif "today" in urgency.lower():
            return now.strftime('%Y-%m-%d 18:00')
        else:
            return (now + pd.Timedelta(days=2)).strftime('%Y-%m-%d %H:%M')

    # Initialize pharmacy data in session state
    if 'pharmacy_transmissions' not in st.session_state:
        st.session_state.pharmacy_transmissions = []

    # Pharmacy Network
    pharmacy_network = {
        "CVS Pharmacy": {"id": "CVS001", "address": "123 Main St, Anytown, USA", "phone": "(555) 123-4567"},
        "Walgreens": {"id": "WAG001", "address": "456 Oak Ave, Somewhere, USA", "phone": "(555) 234-5678"},
        "Walmart Pharmacy": {"id": "WMT001", "address": "789 Pine Rd, Elsewhere, USA", "phone": "(555) 345-6789"},
        "Rite Aid": {"id": "RAD001", "address": "321 Elm St, Nowhere, USA", "phone": "(555) 456-7890"},
        "Kroger Pharmacy": {"id": "KRG001", "address": "654 Maple Dr, Anywhere, USA", "phone": "(555) 567-8901"},
        "Costco Pharmacy": {"id": "CST001", "address": "987 Cedar Ln, Everywhere, USA", "phone": "(555) 678-9012"}
    }

    # Enhanced Prescription Actions
    st.markdown("### ⚡ Prescription Management Actions")

    # Send to Pharmacy Feature
    with st.expander("📤 Send Prescription to Pharmacy", expanded=False):
        st.markdown("#### Select Prescription & Pharmacy")

        col1, col2 = st.columns(2)

        with col1:
            # Prescription selection
            active_prescriptions = [rx for rx in prescriptions if rx['status'] == 'Active']
            if active_prescriptions:
                prescription_options = [f"{rx['id']} - {rx['medication']} ({rx['patient']})"
                                      for rx in active_prescriptions]
                selected_prescription = st.selectbox("Select Prescription to Send",
                                                   prescription_options,
                                                   key="pharmacy_rx_select")
            else:
                st.warning("No active prescriptions available to send.")
                selected_prescription = None

        with col2:
            # Pharmacy selection
            pharmacy_options = list(pharmacy_network.keys())
            selected_pharmacy = st.selectbox("Select Pharmacy",
                                           pharmacy_options,
                                           key="pharmacy_select")

        # Pharmacy details
        if selected_pharmacy:
            pharmacy_info = pharmacy_network[selected_pharmacy]
            st.markdown(f"""
            **📍 Pharmacy Details:**
            - **Address:** {pharmacy_info['address']}
            - **Phone:** {pharmacy_info['phone']}
            - **Network ID:** {pharmacy_info['id']}
            """)

        # Urgency level
        urgency_level = st.selectbox("Urgency Level",
                                   ["Normal (Ready in 1-2 days)",
                                    "Urgent (Ready today)",
                                    "Stat (Ready within 1 hour)"],
                                   key="urgency_select")

        # Additional instructions
        special_instructions = st.text_area("Special Instructions (Optional)",
                                          placeholder="Enter any special handling instructions...",
                                          key="pharmacy_instructions")

        # Send button
        if st.button("📤 Transmit Prescription", use_container_width=True, type="primary"):
            if selected_prescription and selected_pharmacy:
                # Extract prescription details
                rx_id = selected_prescription.split(' - ')[0]
                prescription_details = next((rx for rx in prescriptions if rx['id'] == rx_id), None)

                if prescription_details:
                    # Create transmission record
                    transmission = {
                        'id': f"TX{len(st.session_state.pharmacy_transmissions) + 1:04d}",
                        'prescription_id': rx_id,
                        'patient_name': prescription_details['patient'],
                        'medication': prescription_details['medication'],
                        'dosage': prescription_details['dosage'],
                        'pharmacy': selected_pharmacy,
                        'pharmacy_id': pharmacy_network[selected_pharmacy]['id'],
                        'urgency': urgency_level,
                        'instructions': special_instructions,
                        'status': 'Transmitted',
                        'transmitted_by': st.session_state['name'],
                        'transmitted_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'estimated_ready': _calculate_readiness_time(urgency_level)
                    }

                    st.session_state.pharmacy_transmissions.append(transmission)

                    # Success message with details
                    st.success(f"✅ Prescription successfully transmitted to {selected_pharmacy}!")

                    st.info(f"""
                    **Transmission Details:**
                    - **Transmission ID:** {transmission['id']}
                    - **Estimated Ready Time:** {transmission['estimated_ready']}
                    - **Status:** {transmission['status']}

                    The pharmacy will receive this prescription electronically and contact the patient when ready for pickup.
                    """)

                    # Show pharmacy contact info
                    pharmacy_info = pharmacy_network[selected_pharmacy]
                    st.markdown(f"""
                    **🏥 Pharmacy Contact Information:**
                    - **Address:** {pharmacy_info['address']}
                    - **Phone:** {pharmacy_info['phone']}
                    - **Hours:** Mon-Fri 9AM-9PM, Sat-Sun 9AM-6PM
                    """)
                else:
                    st.error("Error: Could not find prescription details.")
            else:
                st.error("Please select both a prescription and pharmacy.")

    # Transmission History
    if st.session_state.pharmacy_transmissions:
        st.markdown("### 📋 Recent Pharmacy Transmissions")

        # Display recent transmissions (last 10)
        recent_transmissions = st.session_state.pharmacy_transmissions[-10:]

        for tx in reversed(recent_transmissions):
            status_color = {
                'Transmitted': '#2196f3',
                'Received': '#4caf50',
                'Ready': '#ff9800',
                'Picked Up': '#9e9e9e'
            }.get(tx['status'], '#666')

            st.markdown(f"""
            <div style="background: white; padding: 15px; margin: 8px 0; border-radius: 10px; border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0; color: #1f2937;">{tx['medication']}</h4>
                        <p style="margin: 5px 0; color: #6b7280;">Patient: {tx['patient_name']} • Rx ID: {tx['prescription_id']}</p>
                        <p style="margin: 5px 0; color: #374151;">Pharmacy: {tx['pharmacy']} • Ready: {tx['estimated_ready']}</p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">{tx['status']}</span>
                        <p style="margin: 8px 0 0 0; font-size: 0.8rem; color: #666;">TX ID: {tx['id']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Action Buttons Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Write New Rx", use_container_width=True):
            st.info("New prescription form would open here")
    with col2:
        if st.button("🔄 Refill Request", use_container_width=True):
            st.info("Refill request processing would be implemented here")
    with col3:
        transmissions_count = len(st.session_state.pharmacy_transmissions)
        if st.button(f"📤 Pharmacy ({transmissions_count})", use_container_width=True):
            st.info(f"📊 {transmissions_count} prescriptions transmitted to pharmacies")
    with col4:
        st.success("📊 Analytics Dashboard Active")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# --- FEATURE 1: PATIENT RISK SCORE CALCULATOR ---
def calculate_risk_score(patient):
    """Calculate AI-based risk score for a patient"""
    score = 0
    risk_factors = []
    
    # Age factor
    age = patient.get("Age", 0)
    if age > 70:
        score += 30
        risk_factors.append("Advanced age (70+)")
    elif age > 60:
        score += 20
        risk_factors.append("Senior age (60+)")
    elif age > 50:
        score += 10
    
    # Condition severity
    condition = patient.get("MedicalCondition", "")
    if condition in ["Cancer", "Heart Disease", "Stroke"]:
        score += 40
        risk_factors.append(f"Critical condition: {condition}")
    elif condition in ["Diabetes", "Hypertension", "COPD"]:
        score += 25
        risk_factors.append(f"Chronic condition: {condition}")
    elif condition in ["Kidney Disease", "Liver Disease"]:
        score += 30
        risk_factors.append(f"Organ disease: {condition}")
    
    # Length of stay
    stay = patient.get("LengthOfStay", 0)
    if stay > 14:
        score += 15
        risk_factors.append(f"Extended stay ({stay} days)")
    elif stay > 7:
        score += 10
    
    # Billing amount (proxy for treatment complexity)
    billing = patient.get("BillingAmount", 0)
    if billing > 30000:
        score += 15
        risk_factors.append("High treatment cost")
    elif billing > 20000:
        score += 10
    
    # Admission type
    adm_type = patient.get("AdmissionType", "")
    if adm_type == "Emergency":
        score += 20
        risk_factors.append("Emergency admission")
    elif adm_type == "Urgent":
        score += 10
    
    # Determine risk level
    if score >= 70:
        risk_level = "Critical"
        color = "#ef4444"
        icon = "🔴"
    elif score >= 50:
        risk_level = "High"
        color = "#f59e0b"
        icon = "🟠"
    elif score >= 30:
        risk_level = "Medium"
        color = "#eab308"
        icon = "🟡"
    else:
        risk_level = "Low"
        color = "#10b981"
        icon = "🟢"
    
    return {
        "score": min(score, 100),
        "level": risk_level,
        "color": color,
        "icon": icon,
        "factors": risk_factors
    }

# Store risk calculation function in session state for use across pages
if "calculate_risk_score" not in st.session_state:
    st.session_state.calculate_risk_score = calculate_risk_score

# --- PAGE 7: HOSPITAL LOCATIONS MAP ---
if page == "🗺️ Hospital Locations":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">🗺️ Hospital Network Locations</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Interactive map of all healthcare facilities</p>
        </div>
    """, unsafe_allow_html=True)

    # Hospital location data
    hospital_locations = {
        "Apollo Hospital Delhi": {"lat": 28.5494, "lon": 77.2001, "patients": 245, "beds": 500, "type": "Multi-specialty"},
        "AIIMS New Delhi": {"lat": 28.5672, "lon": 77.2100, "patients": 412, "beds": 2478, "type": "Government"},
        "Fortis Hospital Noida": {"lat": 28.5355, "lon": 77.3910, "patients": 189, "beds": 350, "type": "Private"},
        "Max Hospital Saket": {"lat": 28.5244, "lon": 77.2066, "patients": 298, "beds": 400, "type": "Private"},
        "Medanta Gurugram": {"lat": 28.4595, "lon": 77.0266, "patients": 356, "beds": 1250, "type": "Multi-specialty"},
        "BLK Hospital Delhi": {"lat": 28.6517, "lon": 77.1889, "patients": 167, "beds": 650, "type": "Super-specialty"}
    }

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    total_patients = sum(h["patients"] for h in hospital_locations.values())
    total_beds = sum(h["beds"] for h in hospital_locations.values())
    avg_occupancy = (total_patients / total_beds * 100) if total_beds > 0 else 0
    
    col1.metric("Total Facilities", len(hospital_locations))
    col2.metric("Total Beds", f"{total_beds:,}")
    col3.metric("Active Patients", f"{total_patients:,}")
    col4.metric("Avg Occupancy", f"{avg_occupancy:.1f}%")

    st.markdown("---")

    # Create map data
    map_data = []
    for name, info in hospital_locations.items():
        map_data.append({
            "Hospital": name,
            "lat": info["lat"],
            "lon": info["lon"],
            "Patients": info["patients"],
            "Beds": info["beds"],
            "Type": info["type"],
            "Occupancy": f"{info['patients']/info['beds']*100:.1f}%"
        })
    
    map_df = pd.DataFrame(map_data)

    # Plotly scatter map
    st.markdown("### 🗺️ Interactive Hospital Map")
    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="Hospital",
        hover_data={"lat": False, "lon": False, "Patients": True, "Beds": True, "Type": True, "Occupancy": True},
        color="Patients",
        size="Beds",
        color_continuous_scale="Reds",
        size_max=30,
        zoom=9,
        height=600
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Hospital details table
    st.markdown("### 🏥 Hospital Network Details")
    st.dataframe(
        map_df[["Hospital", "Type", "Beds", "Patients", "Occupancy"]],
        use_container_width=True,
        column_config={
            "Hospital": st.column_config.TextColumn("Hospital Name", width="large"),
            "Type": st.column_config.TextColumn("Type", width="medium"),
            "Beds": st.column_config.NumberColumn("Total Beds", width="small"),
            "Patients": st.column_config.NumberColumn("Active Patients", width="small"),
            "Occupancy": st.column_config.TextColumn("Occupancy Rate", width="small")
        }
    )

    # Patient distribution by hospital
    st.markdown("### 📊 Patient Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_patients = px.bar(
            map_df.sort_values("Patients", ascending=False),
            x="Hospital",
            y="Patients",
            color="Patients",
            color_continuous_scale="Blues",
            title="Patients by Hospital"
        )
        fig_patients.update_layout(xaxis_tickangle=-30, showlegend=False, height=350)
        st.plotly_chart(fig_patients, use_container_width=True)
    
    with col2:
        fig_occupancy = px.pie(
            map_df,
            names="Hospital",
            values="Patients",
            title="Patient Share by Hospital",
            hole=0.4
        )
        fig_occupancy.update_layout(height=350)
        st.plotly_chart(fig_occupancy, use_container_width=True)

# --- PAGE 8: DOCTOR SCHEDULE / AVAILABILITY CALENDAR ---
elif page == "👨‍⚕️ Doctor Schedule":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">👨‍⚕️ Doctor Schedule & Availability</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">Weekly calendar and workload management</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize doctor schedule in session state
    if "doctor_schedules" not in st.session_state:
        # Mock doctor schedule data
        doctors = df["Doctor"].unique().tolist()[:10]
        st.session_state.doctor_schedules = {}
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        time_slots = ["09:00-12:00", "12:00-15:00", "15:00-18:00", "18:00-21:00"]
        
        for doctor in doctors:
            st.session_state.doctor_schedules[doctor] = {
                "specialty": np.random.choice(["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General Medicine"]),
                "patients_today": np.random.randint(5, 25),
                "schedule": {}
            }
            
            for day in days:
                available_slots = np.random.choice(time_slots, size=np.random.randint(1, 4), replace=False).tolist()
                st.session_state.doctor_schedules[doctor]["schedule"][day] = available_slots

    # Doctor selection
    selected_doctor = st.selectbox("👨‍⚕️ Select Doctor", list(st.session_state.doctor_schedules.keys()))
    
    doctor_info = st.session_state.doctor_schedules[selected_doctor]
    
    # Doctor info cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Specialty", doctor_info["specialty"])
    col2.metric("Patients Today", doctor_info["patients_today"])
    col3.metric("Weekly Slots", sum(len(slots) for slots in doctor_info["schedule"].values()))
    col4.metric("Status", "🟢 Available" if doctor_info["patients_today"] < 20 else "🟡 Busy")

    st.markdown("---")

    # Weekly schedule calendar
    st.markdown(f"### 📅 Weekly Schedule for Dr. {selected_doctor}")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day in days:
        slots = doctor_info["schedule"].get(day, [])
        
        if slots:
            slot_badges = " ".join([f'<span style="background: #4facfe; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-right: 8px;">{slot}</span>' for slot in slots])
            status_color = "#10b981"
            status_text = "Available"
        else:
            slot_badges = '<span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;">Off Duty</span>'
            status_color = "#ef4444"
            status_text = "Off"
        
        st.markdown(f"""
            <div style="background: white; padding: 15px 20px; margin: 8px 0; border-radius: 10px; border-left: 4px solid {status_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.1rem; color: #1f2937;">{day}</strong>
                        <div style="margin-top: 8px;">{slot_badges}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: {status_color}; font-weight: bold;">{status_text}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # All doctors availability summary
    st.markdown("### 👥 All Doctors Availability Summary")
    
    summary_data = []
    for doctor, info in st.session_state.doctor_schedules.items():
        total_slots = sum(len(slots) for slots in info["schedule"].values())
        summary_data.append({
            "Doctor": doctor,
            "Specialty": info["specialty"],
            "Patients Today": info["patients_today"],
            "Weekly Slots": total_slots,
            "Workload": "High" if info["patients_today"] > 18 else "Medium" if info["patients_today"] > 12 else "Low"
        })
    
    summary_df = pd.DataFrame(summary_data).sort_values("Patients Today", ascending=False)
    
    st.dataframe(
        summary_df,
        use_container_width=True,
        column_config={
            "Doctor": st.column_config.TextColumn("Doctor Name", width="large"),
            "Specialty": st.column_config.TextColumn("Specialty", width="medium"),
            "Patients Today": st.column_config.NumberColumn("Patients Today", width="small"),
            "Weekly Slots": st.column_config.NumberColumn("Weekly Slots", width="small"),
            "Workload": st.column_config.TextColumn("Workload", width="small")
        }
    )

    # Workload distribution chart
    st.markdown("### 📊 Doctor Workload Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_workload = px.bar(
            summary_df,
            x="Doctor",
            y="Patients Today",
            color="Workload",
            color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
            title="Patients per Doctor Today"
        )
        fig_workload.update_layout(xaxis_tickangle=-30, height=350)
        st.plotly_chart(fig_workload, use_container_width=True)
    
    with col2:
        fig_specialty = px.pie(
            summary_df,
            names="Specialty",
            values="Patients Today",
            title="Patients by Specialty",
            hole=0.4
        )
        fig_specialty.update_layout(height=350)
        st.plotly_chart(fig_specialty, use_container_width=True)

st.caption(f"🛡️ CareFlow Secure Session | User: {st.session_state['name']} (@{st.session_state['username']}) | Last Heartbeat: {pd.Timestamp.now().strftime('%H:%M:%S')}")
