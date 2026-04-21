import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import os

# Page Configuration
st.set_page_config(page_title="Healthcare AI Dashboard", page_icon="🏥", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .css-1r6slb0 { /* Sidebar width */
        width: 300px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    .prediction-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not os.path.exists("healthcare.db"):
        return None
    conn = sqlite3.connect("healthcare.db")
    df = pd.read_sql_query("SELECT * FROM ClinicalData", conn)
    conn.close()
    if 'DateofAdmission' in df.columns:
        df['DateofAdmission'] = pd.to_datetime(df['DateofAdmission'])
    if 'DischargeDate' in df.columns:
        df['DischargeDate'] = pd.to_datetime(df['DischargeDate'])
    return df

# Initialize Data
df = load_data()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
    st.title("CareFlow AI")
    st.divider()
    page = st.radio("Navigation", ["📊 Executive Analytics", "🤖 AI Disease Predictor"], index=0)
    st.divider()
    st.info("CareFlow AI uses advanced machine learning to provide clinical insights and risk assessments.")

if df is None:
    st.error("Hospital database not found. Please run the data pipeline first.")
    st.stop()

# --- PAGE: EXECUTIVE ANALYTICS ---
if page == "📊 Executive Analytics":
    st.title("🏥 Healthcare Performance Dashboard")
    st.markdown("### Interactive Insights from Patient Demographics & Clinical Outcomes")
    st.divider()

    # Filters
    with st.sidebar:
        st.header("🔍 Filter Analytics")
        medical_condition = st.multiselect(
            "Medical Condition",
            options=df["MedicalCondition"].unique(),
            default=df["MedicalCondition"].unique()
        )
        admission_type = st.multiselect(
            "Admission Type",
            options=df["AdmissionType"].unique(),
            default=df["AdmissionType"].unique()
        )
        gender = st.multiselect(
            "Gender",
            options=df["Gender"].unique(),
            default=df["Gender"].unique()
        )

    # Apply Filters
    df_selection = df.query(
        "MedicalCondition == @medical_condition & AdmissionType == @admission_type & Gender == @gender"
    )

    # Metrics
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

    # Charts Row 1
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("#### Patient Distribution by Condition")
        fig_condition = px.bar(
            df_selection.groupby("MedicalCondition").size().reset_index(name="Count"),
            x="MedicalCondition", y="Count", color="MedicalCondition",
            template="plotly_white", color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig_condition, use_container_width=True)

    with r1c2:
        st.markdown("#### Billing Amount vs Patient Age")
        fig_age_billing = px.scatter(
            df_selection.sample(min(2000, len(df_selection))),
            x="Age", y="BillingAmount", color="AdmissionType",
            template="plotly_white", opacity=0.6, trendline="ols"
        )
        st.plotly_chart(fig_age_billing, use_container_width=True)

    # Charts Row 2
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("#### Insurance Provider Breakdown")
        fig_insurance = px.pie(df_selection, names="InsuranceProvider", hole=0.5)
        st.plotly_chart(fig_insurance, use_container_width=True)

    with r2c2:
        st.markdown("#### Length of Stay by Medical Condition")
        fig_stay = px.box(df_selection, x="MedicalCondition", y="LengthOfStay", color="MedicalCondition")
        st.plotly_chart(fig_stay, use_container_width=True)

    with st.expander("📄 View Raw Data Snippet"):
        st.dataframe(df_selection.head(100), use_container_width=True)

# --- PAGE: AI DISEASE PREDICTOR ---
elif page == "🤖 AI Disease Predictor":
    st.title("🤖 AI Diagnostic Center")
    st.markdown("### Predict Patient Risk Profiles using Synthetic Health Intelligence")
    st.divider()

    # Load Model Assets
    try:
        model = joblib.load('disease_model.pkl')
        le_gender = joblib.load('le_gender.pkl')
        le_blood = joblib.load('le_blood.pkl')
        le_condition = joblib.load('le_condition.pkl')
        metadata = joblib.load('model_metadata.pkl')
    except Exception as e:
        st.warning("Prediction model not found. Please ensure `train_ai_model.py` has been run.")
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
        st.header("👤 Patient Particulars")
        
        age = st.slider("Patient Age", 0, 100, 45)
        gender = st.selectbox("Gender", options=metadata['genders'])
        blood_type = st.selectbox("Blood Type", options=metadata['blood_types'])
        
        predict_btn = st.button("Generate AI Risk Analysis")
        st.markdown('</div>', unsafe_allow_html=True)

    if predict_btn:
        # Prepare input
        gender_encoded = le_gender.transform([gender])[0]
        blood_encoded = le_blood.transform([blood_type])[0]
        
        input_data = np.array([[age, gender_encoded, blood_encoded]])
        
        # Get Probabilities
        probs = model.predict_proba(input_data)[0]
        prediction_df = pd.DataFrame({
            'Condition': le_condition.classes_,
            'Probability': probs * 100
        }).sort_values('Probability', ascending=False)

        with col2:
            st.markdown(f"#### Risk Assessment for a {age}-year-old {gender} (Type {blood_type})")
            
            # Top Prediction Highlight
            top_condition = prediction_df.iloc[0]['Condition']
            top_prob = prediction_df.iloc[0]['Probability']
            
            st.success(f"**Highest Potential Risk:** {top_condition} ({top_prob:.1f}%)")

            # Radar Chart or Bar Chart for Probabilities
            fig_probs = px.bar(
                prediction_df, 
                x='Probability', 
                y='Condition', 
                orientation='h',
                color='Probability',
                color_continuous_scale='RdYlGn_r',
                range_x=[0, 100],
                text_auto='.1f'
            )
            fig_probs.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_probs, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 💡 AI Recommendations")
            if top_prob > 20:
                st.warning(f"Patient shows elevated patterns for **{top_condition}**. Consider routine screening and lifestyle modification.")
            else:
                st.info("Risk profiles are relatively balanced. Recommend standard annual checkups.")

    else:
        with col2:
            st.info("👈 Enter patient details and click 'Generate' to see the AI risk analysis.")
            # Show some static insight
            st.image("https://img.freepik.com/premium-vector/artificial-intelligence-healthcare-concept-vector-illustration-doctor-using-ai-diagnose-disease_1253202-60194.jpg", use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2026 CareFlow AI | Clinical Research Demonstration Only")
