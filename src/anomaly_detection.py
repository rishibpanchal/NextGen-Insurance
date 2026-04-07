import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

def build_anomaly_detector(df, feature_cols, model_dir='models'):
    """Train Anomaly Detection Model."""
    X = df[feature_cols]
    
    # Isolation Forest
    model = IsolationForest(
        n_estimators=150, 
        max_samples='auto', 
        contamination=float(0.05), # Assume approx 5% outliers
        random_state=42
    )
    
    model.fit(X)
    
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'iso_forest.pkl'))
    
    return model

def detect_anomalies(df, feature_cols, model_dir='models'):
    """Apply anomaly detection."""
    X = df[feature_cols]
    
    try:
        model = joblib.load(os.path.join(model_dir, 'iso_forest.pkl'))
    except FileNotFoundError:
        print("Anomaly detection model not found. Training a new one...")
        model = build_anomaly_detector(df, feature_cols, model_dir)
        
    df = df.copy()
    
    # Predict Anomalies: -1 is outlier, 1 is inlier
    preds = model.predict(X)
    raw_scores = model.decision_function(X)
    
    # Convert prediction to 1=Anomaly, 0=Normal
    df['is_anomaly'] = np.where(preds == -1, 1, 0)
    
    # Normalize score between 0 and 1, where 1 is highly anomalous
    # Decision function returns normally negative for outliers and positive for inliers
    # So we invert and min/max scale purely for ranking risk
    min_score = raw_scores.min()
    max_score = raw_scores.max()
    normalized_scores = (max_score - raw_scores) / (max_score - min_score)
    
    df['anomaly_score'] = normalized_scores
    
    return df, ['is_anomaly', 'anomaly_score']

if __name__ == '__main__':
    from feature_engineering import prepare_features
    from data_preprocessing import preprocess_pipeline
    
    print("Testing Anomaly Detection...")
    df = preprocess_pipeline('data/raw/insurance_claims.csv')
    df_engineered, f_cols = prepare_features(df, is_training=True)
    
    df_out, a_cols = detect_anomalies(df_engineered, f_cols)
    print(df_out[['claim_id', 'claim_amount', 'past_claims', 'anomaly_score', 'is_anomaly']].head(10))
    print(f"Total anomalies detected: {df_out['is_anomaly'].sum()} / {len(df_out)}")