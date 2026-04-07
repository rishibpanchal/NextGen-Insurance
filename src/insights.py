import pandas as pd
import numpy as np
import joblib
import os

def get_feature_importances(model_dir='models', top_n=5):
    """Retrieve top feature importances from trained tree model."""
    try:
        model = joblib.load(os.path.join(model_dir, 'rf_risk_model.pkl'))
        importances = model.feature_importances_
        feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else []
        
        if len(feature_names) > 0:
            feat_imp_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importances
            }).sort_values('Importance', ascending=False)
            
            return feat_imp_df.head(top_n)
        else:
            return pd.DataFrame()
    except FileNotFoundError:
        return pd.DataFrame()

def generate_text_insights(df):
    """Generate dynamic insights based on dataset analytics."""
    insights = []
    
    # Claim size anomaly insights
    high_risk_df = df[df['risk_category'] == 'High Risk']
    
    if len(high_risk_df) > 0:
        avg_high_risk_amt = high_risk_df['claim_amount'].mean()
        avg_normal_amt = df[df['risk_category'] != 'High Risk']['claim_amount'].mean()
        
        diff = ((avg_high_risk_amt - avg_normal_amt) / avg_normal_amt) * 100
        
        insights.append(f"High risk claims are on average {diff:.1f}% more expensive than normal claims.")
        
    # Anomaly insights
    anomalous = df[df['is_anomaly'] == 1]
    if len(anomalous) > 0:
        insights.append(f"Detected {len(anomalous)} mathematically anomalous claims using Isolation Forest.")
        
    # NLP Insights
    suspicious = df[df['has_suspicious_phrases'] == 1]
    if len(suspicious) > 0:
        insights.append(f"Found {len(suspicious)} claims containing known vague or suspicious phrasing.")
        
    # High frequency triggers
    freq_claims = df[df['claim_frequency'] > 3]
    high_risk_freq = freq_claims[freq_claims['risk_category'] == 'High Risk']
    
    if len(freq_claims) > 0:
        ptg = (len(high_risk_freq) / len(freq_claims)) * 100
        insights.append(f"Customers with >3 claims: {ptg:.1f}% were classified as High Risk.")
        
    return insights

if __name__ == '__main__':
    # Ensure processed data exists
    if os.path.exists('data/processed/fully_scored_claims.csv'):
        df = pd.read_csv('data/processed/fully_scored_claims.csv')
        print("--- Feature Importances ---")
        print(get_feature_importances())
        
        print("\n--- Key Insights ---")
        for ins in generate_text_insights(df):
            print(f"- {ins}")
    else:
        print("Please run data pipeline first.")
