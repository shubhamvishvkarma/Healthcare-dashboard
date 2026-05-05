import pandas as pd
from database_config import engine
import sys

def verify_integration():
    print("Testing Professional Database Integration...")
    try:
        # Test connection
        with engine.connect() as conn:
            print(f"Connection Successful!")
            print(f"Driver: {engine.driver}")
            
            # Test data retrieval
            df = pd.read_sql_query("SELECT * FROM ClinicalData LIMIT 5", conn)
            print(f"Sample Data (Top 5 rows):")
            print(df[['Name', 'Age', 'MedicalCondition']])
            print(f"Data loading verified via SQLAlchemy Engine.")
            
    except Exception as e:
        print(f"Integration Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_integration()
