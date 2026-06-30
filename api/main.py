from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.database import get_db, ScoredClaim
from api.pii_redactor import redactor
import logging
import io
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pandas as pd
import uvicorn
from pathlib import Path

from src.risk_engine import RiskEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Insurance Risk API", description="API for predicting claim risk scores.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development. In production, restrict to Vercel domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
risk_engine_instance = None
BASE_DIR = Path(__file__).resolve().parent.parent

class ClaimRequest(BaseModel):
    claim_amount: float
    claim_type: str
    customer_age: int
    claim_description: str
    past_claims: int = 0
    claim_frequency: int = 1
    kyc_verified: bool = True # Onboard IQ alignment

# Initialize the global engine instance (singleton)
engine: Optional[RiskEngine] = None

class TopDriver(BaseModel):
    feature: str
    importance: float

class PredictResponse(BaseModel):
    risk_score: float
    risk_category: str
    top_drivers: List[TopDriver]
    anomaly_flag: bool
    explanation: str

@app.on_event("startup")
def load_models():
    global engine
    logger.info("Loading RiskEngine globally...")
    try:
        model_dir = BASE_DIR / "models"
        engine = RiskEngine.load(model_dir=model_dir)
        logger.info("Models loaded successfully!")
    except Exception as e:
        logger.exception("Warning: Could not load models during startup")
        engine = None

@app.post("/predict-risk")
def predict_risk(request: ClaimRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="Risk Engine model is not loaded yet.")
    
    try:
        # DPDP Privy Alignment: Redact PII before processing
        original_text = request.claim_description
        redacted_text = redactor.redact(original_text)
        
        # Prepare data for prediction
        input_data = pd.DataFrame([{
            'claim_amount': request.claim_amount,
            'claim_type': request.claim_type,
            'customer_age': request.customer_age,
            'claim_description': redacted_text,
            'past_claims': request.past_claims,
            'claim_frequency': request.claim_frequency,
            'location': "NY", # default for model
            'claim_date': "2026-04-08" # default for model
        }])
        
        # Run inference
        ml_probs, anomaly_scores, nlp_scores = engine.predict_features(input_data)
        
        # Calculate risk score (simplified combined logic for API)
        # Using 60% ML, 40% NLP logic similar to processing script
        risk_score = float((ml_probs[0] * 0.6) + (nlp_scores[0] * 0.4))
        
        # Onboard IQ Alignment: KYC AML Override
        if not request.kyc_verified:
            category = "High"
            action = "ACTION: Route to SIU (Failed KYC/AML)"
            risk_score = max(risk_score, 0.95) # Force high score
        else:
            if risk_score > 0.7 or anomaly_scores[0] == -1:
                category = "High"
                action = "ACTION: Route to SIU Fraud Investigators"
            elif risk_score > 0.4:
                category = "Medium"
                action = "ACTION: Manual Adjuster Review"
            else:
                category = "Low"
                action = "ACTION: Fast-Track Payment (STP)"
        
        # Get SHAP explanations
        top_drivers = engine.get_top_drivers(X=input_data)
        
        return {
            "ml_probability": float(ml_probs[0]),
            "anomaly_score": float(anomaly_scores[0]),
            "nlp_risk_score": float(nlp_scores[0]),
            "combined_risk_score": risk_score,
            "risk_category": category,
            "automated_action": action,
            "top_drivers": top_drivers,
            "redacted_text": redacted_text,
            "kyc_passed": request.kyc_verified
        }
    except Exception as e:
        logger.exception("Error predicting risk")
        # Return generic error to client
        return JSONResponse(status_code=500, content={"message": "Internal Server Error during prediction."})

@app.get("/claims")
def get_claims(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    claims = db.query(ScoredClaim).offset(offset).limit(limit).all()
    # Format for the UI
    results = []
    for c in claims:
        results.append({
            "id": c.claim_id,
            "name": f"Customer {c.customer_id}", # Obfuscating for demo
            "type": c.claim_type,
            "amount": c.claim_amount,
            "risk": c.risk_category,
            "score": c.risk_score
        })
    return {"claims": results}

@app.get("/claims/{claim_id}")
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(ScoredClaim).filter(ScoredClaim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    return {
        "id": claim.claim_id,
        "customer_id": claim.customer_id,
        "type": claim.claim_type,
        "amount": claim.claim_amount,
        "age": claim.customer_age,
        "description": claim.claim_description,
        "past_claims": claim.past_claims,
        "frequency": claim.claim_frequency,
        "risk": claim.risk_category,
        "score": claim.risk_score,
        "ml_prob": claim.ml_probability,
        "nlp_score": claim.nlp_risk_score,
        "anomaly": claim.anomaly_flag
    }

@app.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Calculate KPIs
    total_exposure = db.query(func.sum(ScoredClaim.claim_amount)).scalar() or 0
    avg_settlement = db.query(func.avg(ScoredClaim.claim_amount)).scalar() or 0
    high_risk_count = db.query(func.count(ScoredClaim.claim_id)).filter(ScoredClaim.risk_category == "High").scalar() or 0
    anomaly_count = db.query(func.count(ScoredClaim.claim_id)).filter(ScoredClaim.anomaly_flag == True).scalar() or 0

    # Calculate exposure chart data by claim_type
    categories = db.query(
        ScoredClaim.claim_type, 
        func.sum(ScoredClaim.claim_amount).label('exposure')
    ).group_by(ScoredClaim.claim_type).all()
    
    # Calculate risk part of exposure (just a simple heuristic for the chart: high risk amount per category)
    risk_by_cat = db.query(
        ScoredClaim.claim_type,
        func.sum(ScoredClaim.claim_amount).label('risk_amount')
    ).filter(ScoredClaim.risk_category == "High").group_by(ScoredClaim.claim_type).all()
    
    risk_dict = {cat: amt for cat, amt in risk_by_cat}

    chart_data = []
    for cat, exp in categories:
        chart_data.append({
            "name": cat,
            "exposure": float(exp) if exp else 0,
            "risk": float(risk_dict.get(cat, 0))
        })

    return {
        "kpis": {
            "total_exposure": float(total_exposure),
            "avg_settlement": float(avg_settlement),
            "high_risk": high_risk_count,
            "anomalies": anomaly_count
        },
        "chart_data": chart_data
    }

@app.get("/random-claim")
def get_random_claim(db: Session = Depends(get_db)):
    # Grab a random claim from the database
    random_claim = db.query(ScoredClaim).order_by(func.random()).first()
    if not random_claim:
        raise HTTPException(status_code=404, detail="No claims found in DB")
    return {
        "claim_id": random_claim.claim_id,
        "amount": random_claim.claim_amount,
        "type": random_claim.claim_type,
        "age": random_claim.customer_age,
        "description": random_claim.claim_description,
        "past_claims": random_claim.past_claims,
        "frequency": random_claim.claim_frequency
    }

@app.post("/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    """Batch Auto-Adjudication"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Model loading")
    
    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Basic validation
        required = ['claim_amount', 'claim_type', 'customer_age', 'claim_description', 'past_claims', 'claim_frequency']
        if not all(c in df.columns for c in required):
            raise HTTPException(status_code=400, detail="Missing required columns in CSV")
            
        # Optional KYC column check
        if 'kyc_verified' not in df.columns:
            df['kyc_verified'] = True
            
        if 'location' not in df.columns:
            df['location'] = "NY"
            
        if 'claim_date' not in df.columns:
            df['claim_date'] = "2026-04-08"
            
        # Redact PII in batch
        df['claim_description'] = df['claim_description'].fillna("").apply(redactor.redact)
        
        # Predict
        ml_probs, anomaly_scores, nlp_scores = engine.predict_features(df)
        
        results = []
        auto_approved = 0
        manual_review = 0
        fraud_siu = 0
        
        for i in range(len(df)):
            risk = float((ml_probs[i] * 0.6) + (nlp_scores[i] * 0.4))
            kyc = bool(df['kyc_verified'].iloc[i])
            
            if not kyc:
                status = "SIU FRAUD ROUTING"
                fraud_siu += 1
            elif risk > 0.7 or anomaly_scores[i] == -1:
                status = "SIU FRAUD ROUTING"
                fraud_siu += 1
            elif risk > 0.4:
                status = "MANUAL REVIEW"
                manual_review += 1
            else:
                status = "AUTO-APPROVED (STP)"
                auto_approved += 1
                
            results.append({
                "index": i,
                "amount": float(df['claim_amount'].iloc[i]),
                "status": status,
                "risk": risk
            })
            
        return {
            "total_processed": len(df),
            "auto_approved": auto_approved,
            "manual_review": manual_review,
            "fraud_siu": fraud_siu,
            "sample_results": results[:50] # Send back first 50 for table
        }
        
    except Exception as e:
        logger.exception("Batch predict error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)