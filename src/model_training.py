import pandas as pd
import numpy as np
import sqlite3
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

import sys
import os

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.risk_engine import RiskEngine

CONFIG_PATH = BASE_DIR / "config.json"
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

def complete_pipeline(file_path=None):
    from src.data_generation import generate_synthetic_data
    
    print("Starting Model Training Pipeline...")
    
    # 1. Load data
    db_path = BASE_DIR / "data" / CONFIG["database"]["filename"]
    if not db_path.exists():
        print("Database not found. Generating synthetic data...")
        df = generate_synthetic_data()
    else:
        conn = sqlite3.connect(database=str(db_path))
        df = pd.read_sql("SELECT * FROM raw_claims", conn)
        conn.close()
        
    print(f"Loaded {len(df)} records for training.")
    
    # Mandatory Data Leakage Fix: Split before ANY preprocessing
    X = df.drop(columns=['fraud_label'])
    y = df['fraud_label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}")
    
    # 2. Initialize and Train Risk Engine
    engine = RiskEngine()
    engine.fit(X_train, y_train)
    
    # 3. Evaluate Risk Engine (Specifically the ML Component)
    print("\n--- Evaluating Model on Test Data (Strict Isolation) ---")
    
    ml_probs, anomaly_scores, nlp_scores = engine.predict_features(X_test)
    preds = (ml_probs >= 0.5).astype(int)
    
    print("\nClassification Report (ML Classifier):")
    print(classification_report(y_test, preds))
    print(f"ROC AUC: {roc_auc_score(y_test, ml_probs):.4f}")
    
    # 4. Save Model
    model_path = engine.save()
    print(f"\nPipeline complete. Model artifact saved at: {model_path}")
    
if __name__ == "__main__":
    complete_pipeline()