
import pandas as pd
import numpy as np
import sqlite3
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / 'config.json'

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def generate_synthetic_data(num_records=5000):
    np.random.seed(42)
    random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    data = []
    
    locations = ['New York', 'California', 'Texas', 'Florida', 'Illinois', 'Ohio', 'Georgia', 'Remote']
    claim_types = ['Auto', 'Home', 'Health', 'Travel', 'Liability']
    
    vague_texts = [
        'Damage occurred to property.',
        'Lost item during transit.',
        'Injured in an incident.',
        'Fell and hurt myself.',
        'Car accident with another vehicle.',
        'Water leak caused damage.',
        'Stolen electronics.'
    ]

    detailed_texts = [
        'Rear-ended at stop light on Main St by a blue sedan. Bumper cracked.',
        'Roof leak during severe thunderstorm on Tuesday. Water damage to ceiling in living room.',
        'Sprained ankle while hiking on Camelback Mountain. ER visit required.',
        'Flight cancelled due to weather. Rebooked hotel for 2 nights.',
        'Dog bit delivery driver on the leg. Medical expenses covered.',
        'Basement flooded due to burst pipe. 3 inches of water, destroyed carpet.',
        'Laptop stolen from locked car in mall parking lot. Forced entry visible.'
    ]
    
    for i in range(num_records):
        customer_id = f'CUST_{np.random.randint(1000, 5000):04d}'
        claim_id = f'CLM_{i:06d}'
        claim_type = np.random.choice(claim_types, p=[0.4, 0.3, 0.15, 0.1, 0.05])
        
        if claim_type == 'Auto':
            base_amt = np.random.gamma(shape=2, scale=2000)
        elif claim_type == 'Home':
            base_amt = np.random.gamma(shape=2.5, scale=5000)
        elif claim_type == 'Health':
            base_amt = np.random.gamma(shape=1.5, scale=1000)
        else:
            base_amt = np.random.gamma(shape=2, scale=800)

        claim_amount = max(100, round(base_amt, 2))
        days_offset = np.random.randint(0, 730)
        claim_date = start_date + timedelta(days=days_offset)
        customer_age = int(max(18, np.random.normal(45, 15)))
        location = np.random.choice(locations)
        past_claims = np.random.poisson(0.5)

        is_fraud = 0
        rand_val = np.random.random()

        if rand_val < 0.05:
            is_fraud = 1
            if np.random.random() < 0.4:
                claim_amount *= np.random.uniform(2.5, 4.0)
                description = np.random.choice(vague_texts)
            elif np.random.random() < 0.7:
                past_claims += np.random.randint(3, 7)
                customer_age = np.random.randint(18, 25)
                description = np.random.choice(vague_texts)
            else:
                claim_type = 'Liability'
                claim_amount = np.random.uniform(20000, 50000)
                description = np.random.choice(vague_texts)
        else:
            description = np.random.choice(detailed_texts)

        data.append({
            'claim_id': claim_id,
            'customer_id': customer_id,
            'claim_amount': claim_amount,
            'claim_type': claim_type,
            'claim_date': claim_date.strftime('%Y-%m-%d'),
            'customer_age': customer_age,
            'location': location,
            'claim_description': description,
            'past_claims': past_claims,
            'fraud_label': is_fraud
        })

    df = pd.DataFrame(data)
    freq_map = df['customer_id'].value_counts().to_dict()
    df['claim_frequency'] = df['customer_id'].map(freq_map)

    # Save to SQLite
    db_path = Path(CONFIG['database']['path'])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    df.to_sql('raw_claims', conn, if_exists='replace', index=False)
    conn.close()
    
    # Also save to raw CSV for backup
    csv_path = Path(CONFIG['paths']['raw_csv_fallback'])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    
    print(f'Generated {num_records} records.')
    print(f'Saved to {db_path} and {csv_path}')
    return df

if __name__ == '__main__':
    generate_synthetic_data()
