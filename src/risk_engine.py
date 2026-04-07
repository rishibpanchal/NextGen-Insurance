import pandas as pd
import numpy as np
import json
import joblib
import os
from pathlib import Path
from datetime import datetime

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest

class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, feature_names):
        self.feature_names = feature_names
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X[self.feature_names]

class NLPProcessor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words="english", ngram_range=(1,2))
        self.classifier = LogisticRegression(class_weight="balanced", random_state=42)
        
    def fit(self, X, y):
        X_vec = self.vectorizer.fit_transform(X["claim_description"].fillna(""))
        self.classifier.fit(X_vec, y)
        return self
        
    def transform(self, X):
        X_vec = self.vectorizer.transform(X["claim_description"].fillna(""))
        return self.classifier.predict_proba(X_vec)[:, 1]

class RiskEngine:
    def __init__(self, config_path=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config_path = config_path or (self.base_dir / "config.json")
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
            
        self.cat_cols = ["claim_type", "location"]
        self.num_cols = ["claim_amount", "customer_age", "past_claims"]
        
        self.preprocessor = None
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        self.detector = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.nlp_processor = NLPProcessor()
        
        self.anomaly_scaler = MinMaxScaler()
        self.anomaly_threshold = 0.5

    def _build_preprocessor(self):
         return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.cat_cols)
            ]
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        print("Training NLP Processor...")
        self.nlp_processor.fit(X, y)
        
        print("Training ML Preprocessor...")
        self.preprocessor = self._build_preprocessor()
        X_tf = self.preprocessor.fit_transform(X)
        
        print("Training Auto Classifier...")
        self.classifier.fit(X_tf, y)
        
        print("Training Anomaly Detector...")
        self.detector.fit(X_tf)
        
        # Calculate anomaly stats on training
        anomaly_scores = self.detector.decision_function(X_tf)
        a_max = anomaly_scores.max()
        # Invert scores so higher is more anomalous
        scores_inverted = a_max - anomaly_scores
        self.anomaly_scaler.fit(scores_inverted.reshape(-1, 1))
        
        # Determine 95th percentile threshold
        norm_scores = self.anomaly_scaler.transform(scores_inverted.reshape(-1, 1)).flatten()
        self.anomaly_threshold = np.percentile(norm_scores, 95) if len(norm_scores) > 0 else 0.5
        
        return self
        
    def predict_features(self, X: pd.DataFrame):
        X_tf = self.preprocessor.transform(X)
        
        ml_probs = self.classifier.predict_proba(X_tf)[:, 1]
        
        # Process anomalies consistently
        anomaly_scores = self.detector.decision_function(X_tf)
        a_max = self.detector.offset_ if hasattr(self.detector, 'offset_') else 0.0
        scores_inverted = a_max - anomaly_scores
        anomaly_norm = self.anomaly_scaler.transform(scores_inverted.reshape(-1, 1)).flatten()
        anomaly_norm = np.clip(anomaly_norm, 0, 1)
             
        nlp_scores = self.nlp_processor.transform(X)
        return ml_probs, anomaly_norm, nlp_scores
        
    def predict(self, X: pd.DataFrame):
        ml_probs, anomaly_scores, nlp_scores = self.predict_features(X)

        w_ml = self.config["weights"]["ml"]
        w_nlp = self.config["weights"]["nlp"]
        w_anomaly = self.config["weights"]["anomaly"]
        
        composite_score = (ml_probs * w_ml) + (nlp_scores * w_nlp) + (anomaly_scores * w_anomaly)
        composite_score = np.clip(composite_score, 0, 1)
        
        df_out = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
            
        df_out["ml_probability"] = ml_probs
        df_out["anomaly_score"] = anomaly_scores
        df_out["nlp_risk_score"] = nlp_scores
        df_out["risk_score"] = composite_score
        
        t_low = self.config["thresholds"]["low"]
        t_high = self.config["thresholds"]["high"]
        
        conditions = [
            (composite_score < t_low),
            (composite_score >= t_low) & (composite_score < t_high),
            (composite_score >= t_high)
        ]
        choices = ["Low", "Medium", "High"]
        df_out["risk_category"] = np.select(conditions, choices, default="Unknown")
        
        df_out["anomaly_flag"] = anomaly_scores >= self.anomaly_threshold
        
        return df_out
        
    def get_top_drivers(self):
        feature_names = self.preprocessor.get_feature_names_out()
        importances = self.classifier.feature_importances_
        drivers = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        return [{"feature": f, "importance": float(i)} for f, i in drivers[:5]]
        
    def save(self, model_dir=None):
        if model_dir is None:
             model_dir = self.base_dir / "models"
        else:
             model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = model_dir / "risk_engine_artifact.pkl"
        
        joblib.dump(self, model_path)
        
        metadata = {
            "version": version,
            "trained_at": datetime.now().isoformat(),
            "model_path": str(model_path.relative_to(self.base_dir)).replace("\\\\", "/")
        }
        with open(model_dir / "metadata.json", "w") as f:
            json.dump(metadata, f)
            
        print(f"Model saved to {model_path}")
        return model_path
        
    @classmethod
    def load(cls, model_dir=None):
        base_dir = Path(__file__).resolve().parent.parent
        if model_dir is None:
             model_dir = base_dir / "models"
        else:
             model_dir = Path(model_dir)
             
        meta_path = model_dir / "metadata.json"
        
        if meta_path.exists():
            with open(meta_path, "r") as f:
                metadata = json.load(f)
            model_path = base_dir / metadata["model_path"]
        else:
            model_paths = sorted(model_dir.glob("risk_engine_*.pkl"))
            if not model_paths:
                raise FileNotFoundError("No models found.")
            model_path = model_paths[-1]
            
        print(f"Loading model from {model_path}")
        return joblib.load(model_path)
