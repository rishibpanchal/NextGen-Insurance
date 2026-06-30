from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "insurance_risk.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ScoredClaim(Base):
    __tablename__ = "scored_claims"
    
    # Using claim_id as primary key assuming it is unique in the dataset
    claim_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String)
    claim_amount = Column(Float)
    claim_type = Column(String)
    claim_date = Column(String)
    customer_age = Column(Integer)
    location = Column(String)
    claim_description = Column(String)
    past_claims = Column(Integer)
    claim_frequency = Column(Integer)
    
    # ML Outputs
    fraud_label = Column(Integer)
    ml_probability = Column(Float)
    anomaly_score = Column(Float)
    anomaly_flag = Column(Boolean)
    nlp_risk_score = Column(Float)
    risk_score = Column(Float)
    risk_category = Column(String)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
