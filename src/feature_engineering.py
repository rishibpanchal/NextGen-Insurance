import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib
import os

def generate_derived_features(df):
    """Create new features based on domain logic."""
    df = df.copy()
    
    # 1. claim_amount / avg_claim
    avg_claim_by_type = df.groupby('claim_type')['claim_amount'].transform('mean')
    df['amount_vs_avg'] = df['claim_amount'] / avg_claim_by_type
    
    # 2. Add time-based features
    df['claim_month'] = df['claim_date'].dt.month
    df['claim_year'] = df['claim_date'].dt.year
    df['is_weekend'] = df['claim_date'].dt.weekday >= 5
    
    # 3. claims_per_month (proxy: frequency / time span if available, let's use past claims + current freq)
    df['total_claim_activity'] = df['past_claims'] + df['claim_frequency']
    
    # 4. Risk ratios: past claims to age
    df['claims_to_age_ratio'] = df['past_claims'] / (df['customer_age'] + 1) # +1 to avoid division by zero
    
    # Extract text length for simple numerical feature
    df['desc_length'] = df['claim_description'].apply(lambda x: len(str(x).split()))
    
    return df

def setup_feature_pipeline(df, is_training=True, output_dir='models'):
    """Setup and apply StandardScaler and Categorical Encoding."""
    
    # Define columns
    num_cols = ['claim_amount', 'customer_age', 'past_claims', 'claim_frequency', 
                'amount_vs_avg', 'total_claim_activity', 'claims_to_age_ratio', 'desc_length']
    cat_cols = ['claim_type', 'location']
    
    if is_training:
        # Create transformers
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # We will use label encoding manually or one-hot via column transformer
        # For simplicity in outputting dataframe back, let's manually encode
        
        # Save categorical encoders
        le_dict = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col])
            le_dict[col] = le
            
        os.makedirs(output_dir, exist_ok=True)
        joblib.dump(le_dict, os.path.join(output_dir, 'label_encoders.pkl'))
        
        # Fit scaler
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        joblib.dump(scaler, os.path.join(output_dir, 'scaler.pkl'))
        
    else:
        # Load and transform
        le_dict = joblib.load(os.path.join(output_dir, 'label_encoders.pkl'))
        for col in cat_cols:
            # Handle unknown classes by assigning basic transform or standard category
            # For robustness in production, using handle_unknown='ignore' in OneHotEncoder is better
            # Here we wrap LabelEncoder in a try-except for new categories
            le = le_dict[col]
            classes_arr = le.classes_
            df[f'{col}_encoded'] = df[col].apply(lambda x: le.transform([x])[0] if x in classes_arr else 0)
            
        scaler = joblib.load(os.path.join(output_dir, 'scaler.pkl'))
        df[num_cols] = scaler.transform(df[num_cols])
        
    return df, num_cols, [f'{c}_encoded' for c in cat_cols]


def prepare_features(df, is_training=True):
    """Full feature engineering pipeline."""
    df = generate_derived_features(df)
    df, num_features, cat_features = setup_feature_pipeline(df, is_training=is_training)
    
    feature_cols = num_features + cat_features
    return df, feature_cols

if __name__ == '__main__':
    from data_preprocessing import preprocess_pipeline
    
    print("Loading prepared data...")
    df = preprocess_pipeline('data/raw/insurance_claims.csv')
    df_engineered, f_cols = prepare_features(df, is_training=True)
    
    # Save processed data
    os.makedirs('data/processed', exist_ok=True)
    df_engineered.to_csv('data/processed/featured_claims.csv', index=False)
    print(f"Features created: {f_cols}")
    print("Saved processed data to data/processed/featured_claims.csv")
