import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Healthcare Analytics Dashboard", page_icon="🏥", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    conn = sqlite3.connect("healthcare.db")
    df = pd.read_sql_query("SELECT * FROM ClinicalData", conn)
    conn.close()
    # Convert dates
    df['DateofAdmission'] = pd.to_datetime(df['DateofAdmission'])
    df['DischargeDate'] = pd.to_datetime(df['DischargeDate'])
    return df

# Initialize Data
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading database: {e}. Please run the data pipeline first.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Analytics")
medical_condition = st.sidebar.multiselect(
    "Medical Condition",
    options=df["MedicalCondition"].unique(),
    default=df["MedicalCondition"].unique()
)

admission_type = st.sidebar.multiselect(
    "Admission Type",
    options=df["AdmissionType"].unique(),
    default=df["AdmissionType"].unique()
)

gender = st.sidebar.multiselect(
    "Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

# Apply Filters
df_selection = df.query(
    "MedicalCondition == @medical_condition & AdmissionType == @admission_type & Gender == @gender"
)

# --- HEADER ---
st.title("🏥 Healthcare Performance Dashboard")
st.markdown("### Interactive Insights from Patient Demographics & Clinical Outcomes")
st.divider()

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", f"{len(df_selection):,}")
with col2:
    avg_billing = df_selection["BillingAmount"].mean()
    st.metric("Avg Billing Amount", f"${avg_billing:,.2f}")
with col3:
    avg_stay = df_selection["LengthOfStay"].mean()
    st.metric("Avg Length of Stay", f"{avg_stay:.1f} Days")
with col4:
    unique_hosps = df_selection["Hospital"].nunique()
    st.metric("Active Hospitals", f"{unique_hosps}")

st.divider()

# --- CHARTS ROW 1 ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### Patient Distribution by Medical Condition")
    fig_condition = px.bar(
        df_selection.groupby("MedicalCondition").size().reset_index(name="Count"),
        x="MedicalCondition",
        y="Count",
        color="MedicalCondition",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    st.plotly_chart(fig_condition, width="stretch")

with row1_col2:
    st.markdown("#### Billing Amount vs Patient Age")
    fig_age_billing = px.scatter(
        df_selection.sample(min(2000, len(df_selection))), # Sample for performance
        x="Age",
        y="BillingAmount",
        color="AdmissionType",
        hover_data=["MedicalCondition"],
        template="plotly_white",
        opacity=0.6,
        trendline="ols"
    )
    st.plotly_chart(fig_age_billing, width="stretch")

# --- CHARTS ROW 2 ---
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### Insurance Provider Breakdown")
    fig_insurance = px.pie(
        df_selection,
        names="InsuranceProvider",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_insurance, width="stretch")

with row2_col2:
    st.markdown("#### Length of Stay by Medical Condition")
    fig_stay = px.box(
        df_selection,
        x="MedicalCondition",
        y="LengthOfStay",
        color="MedicalCondition",
        template="plotly_white"
    )
    st.plotly_chart(fig_stay, width="stretch")

# --- DATA TABLE ---
with st.expander("📄 View Raw Data Snippet"):
    st.dataframe(df_selection.head(100), width="stretch")

# Footer
st.markdown("---")
