import pandas as pd
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / "data" / "insurance_risk.db"
csv_path = BASE_DIR / "data" / "processed" / "fully_scored_claims.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path)
    
    # We might want to rename some columns if they are not clean, but pandas to_sql handles this well.
    # Connect to SQLite
    conn = sqlite3.connect(database=str(db_path))
    
    # Write to table 'scored_claims'
    df.to_sql("scored_claims", conn, if_exists="replace", index=False)
    
    conn.close()
    print(f"Successfully migrated {len(df)} scored claims to the database.")
else:
    print(f"Error: {csv_path} does not exist.")
