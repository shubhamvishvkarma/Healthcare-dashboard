import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_model():
    print("Starting AI Model Training...")
    
    # Load data from the database
    if not os.path.exists("healthcare.db"):
        print("Error: healthcare.db not found. Run data_pipeline.py first.")
        return

    conn = sqlite3.connect("healthcare.db")
    df = pd.read_sql_query("SELECT Age, Gender, BloodType, MedicalCondition FROM ClinicalData", conn)
    conn.close()

    print(f"Loaded {len(df)} records for training.")

    # Categorical Encoding
    le_gender = LabelEncoder()
    df['Gender_Encoded'] = le_gender.fit_transform(df['Gender'])

    le_blood = LabelEncoder()
    df['BloodType_Encoded'] = le_blood.fit_transform(df['BloodType'])

    le_condition = LabelEncoder()
    df['Condition_Encoded'] = le_condition.fit_transform(df['MedicalCondition'])

    # Feature selection
    X = df[['Age', 'Gender_Encoded', 'BloodType_Encoded']]
    y = df['Condition_Encoded']

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train Model
    # Using RandomForest for robust classification
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Calculate Accuracy
    accuracy = model.score(X_test, y_test)
    print(f"Model Training Complete. Accuracy: {accuracy:.2%}")

    # Save Model and Encoders
    joblib.dump(model, 'disease_model.pkl')
    joblib.dump(le_gender, 'le_gender.pkl')
    joblib.dump(le_blood, 'le_blood.pkl')
    joblib.dump(le_condition, 'le_condition.pkl')
    
    # Save feature names and classes for easy access
    metadata = {
        'conditions': le_condition.classes_.tolist(),
        'genders': le_gender.classes_.tolist(),
        'blood_types': le_blood.classes_.tolist()
    }
    joblib.dump(metadata, 'model_metadata.pkl')

    print("Model and assets saved to disk.")

if __name__ == "__main__":
    train_model()
