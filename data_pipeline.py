import pandas as pd
import sqlite3
import os

# Data Source: High-quality mirror of Kaggle's Healthcare Dataset
DATA_URL = "https://raw.githubusercontent.com/imranbdcse/healthcaredatasets/master/healthcare_dataset.csv"
DB_PATH = "healthcare.db"
EXCEL_PATH = "Healthcare_Data.xlsx"
POWERBI_PATH = "PowerBI_Export.csv"

def fetch_and_process_data():
    print(f"Fetching healthcare data from {DATA_URL}...")
    try:
        df = pd.read_csv(DATA_URL)
        print("Data fetched successfully!")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    print("Cleaning and processing data...")
    # Convert date columns to datetime objects
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    
    # Calculate Length of Stay (a key performance metric for Power BI) - cast to integer
    df['LengthOfStay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days.astype(int)
    
    # Standardize column names for SQL (remove spaces)
    df.columns = [c.replace(' ', '') for c in df.columns]
    
    # Handle missing values if any (though this dataset is usually clean)
    df = df.fillna('Unknown')
    
    return df

def save_to_sql_and_export(df):
    if df is None:
        return

    print(f"Connecting to SQLite Database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # Save to SQLite
    print("Writing clinical data to SQL...")
    df.to_sql('ClinicalData', conn, if_exists='replace', index=False)
    
    # Create a Performance Summary View for Power BI
    # This aggregates data by Medical Condition and Insurance Provider
    query = """
    SELECT MedicalCondition, InsuranceProvider, 
           COUNT(*) as PatientCount, 
           AVG(BillingAmount) as AvgBilling, 
           AVG(LengthOfStay) as AvgStay
    FROM ClinicalData
    GROUP BY MedicalCondition, InsuranceProvider
    """
    df_summary = pd.read_sql_query(query, conn)
    df_summary.to_sql('PerformanceSummary', conn, if_exists='replace', index=False)
    
    conn.close()
    
    # Save to Excel for traditional reporting
    print(f"Exporting to Excel at {EXCEL_PATH}...")
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='AllData', index=False)
        df_summary.to_excel(writer, sheet_name='PerformanceMetrics', index=False)
        
    # Export Power BI optimized CSV
    print(f"Exporting Power BI CSV at {POWERBI_PATH}...")
    df.to_csv(POWERBI_PATH, index=False)
    
    print("\nPipeline execution completed successfully!")
    print(f"- Total Records processed: {len(df)}")
    print(f"- SQLite Table created: ClinicalData")
    print(f"- Power BI CSV generated: {POWERBI_PATH}")

if __name__ == "__main__":
    healthcare_df = fetch_and_process_data()
    save_to_sql_and_export(healthcare_df)
