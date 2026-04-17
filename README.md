# Healthcare Performance & Analytics Dashboard 🏥

A comprehensive data engineering and visualization project that transforms raw healthcare records into high-impact executive insights.

## 🚀 Overview
This repository contains a full-stack data pipeline designed to handle large clinical datasets and provide actionable insights for hospital administration and clinical researchers.

**Key Capabilities:**
*   **Automated Data Pipeline**: Fetches real-world datasets, cleans noisy clinical records, and calculates derived metrics like *Length of Stay (LoS)*.
*   **SQL Persistence**: Robust data storage using SQLite for local development and analysis.
*   **Premium Interactive Dashboard**: A professional-grade web application for real-time data exploration and executive reporting.
*   **BI Readiness**: Optimized exports for integration with Power BI and Excel.

## 🛠️ Tech Stack
*   **Data Processing**: Python, Pandas
*   **Database**: SQLite3, SQL
*   **Visualization**: Streamlit, Plotly, Seaborn
*   **Analytics**: Statsmodels (OLS Mapping & Trendlines)

## 📊 Dashboard Features
*   **Executive Metrics**: Instant visibility into Patient Volume, Revenue, and Efficiency.
*   **Clinical Deep-Dives**: Analyze patient distribution across conditions (Cancer, Diabetes, Obesity, etc.).
*   **Financial Insights**: Correlation analysis of Billing Amounts vs. Patient Demographics.
*   **Hospital Benchmarking**: Length of stay comparisons across medical conditions.

## 📖 How to Run

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Installation
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install pandas streamlit plotly statsmodels openpyxl
```

### 3. Generate the Database
Execute the pipeline to fetch the dataset and build the `healthcare.db` file:
```bash
python data_pipeline.py
```

### 4. Launch the Dashboard
```bash
streamlit run dashboard.py
```

## 📄 License
This project is for educational and clinical research demonstration purposes.
