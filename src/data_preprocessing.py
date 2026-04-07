import pandas as pd
import numpy as np

def load_data(file_path):
    """Load raw dataset."""
    return pd.read_csv(file_path)

def clean_data(df):
    """Handle missing values and correct data types."""
    df = df.copy()
    
    # Convert dates
    df['claim_date'] = pd.to_datetime(df['claim_date'])
    
    # Fill missing values
    df['customer_age'] = df['customer_age'].fillna(df['customer_age'].median())
    df['claim_amount'] = df['claim_amount'].fillna(df['claim_amount'].mean())
    df['past_claims'] = df['past_claims'].fillna(0)
    
    # Fill missing text
    df['claim_description'] = df['claim_description'].fillna("No description provided.")
    
    return df

def preprocess_pipeline(file_path):
    """Full preprocessing pipeline."""
    df = load_data(file_path)
    df = clean_data(df)
    return df

if __name__ == '__main__':
    df = preprocess_pipeline('data/raw/insurance_claims.csv')
    print(df.info())
