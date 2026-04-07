from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
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
risk_engine_instance = None
BASE_DIR = Path(__file__).resolve().parent.parent

class ClaimInput(BaseModel):
    claim_id: str
    customer_id: str
    claim_amount: float
    claim_type: str
    claim_date: str
    customer_age: int
    location: str
    claim_description: str
    past_claims: int
    claim_frequency: int

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
    global risk_engine_instance
    logger.info("Loading RiskEngine globally...")
    try:
        model_dir = BASE_DIR / "models"
        risk_engine_instance = RiskEngine.load(model_dir=model_dir)
        logger.info("Models loaded successfully!")
    except Exception as e:
        logger.exception("Warning: Could not load models during startup")
        risk_engine_instance = None

@app.post("/predict-risk", response_model=PredictResponse)
def predict_risk(claim: ClaimInput):
    """Predict risk for a single insurance claim."""
    global risk_engine_instance
    if risk_engine_instance is None:
         raise HTTPException(status_code=500, detail="RiskEngine is not loaded. Train the model first.")
         
    try:
        df = pd.DataFrame([claim.model_dump()])
        df_final = risk_engine_instance.predict(df)
        result = df_final.iloc[0].to_dict()

        top_drivers = risk_engine_instance.get_top_drivers()

        explanation = f"Risk evaluated as {result['risk_category']} with composite score of {result['risk_score']:.3f}. "
        if result.get('nlp_risk_score', 0) > 0.5:
            explanation += "Suspicious language flagged. "
        if result.get('anomaly_flag', False):
            explanation += "Claim flagged as mathematical anomaly. "

        return PredictResponse(
            risk_score=float(round(result["risk_score"], 3)),
            risk_category=str(result["risk_category"]),
            top_drivers=top_drivers,
            anomaly_flag=bool(result["anomaly_flag"]),
            explanation=explanation
        )

    except Exception as e:
        logger.exception("Error predicting risk")
        # Return generic error to client
        return JSONResponse(status_code=500, content={"message": "Internal Server Error during prediction."})

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)