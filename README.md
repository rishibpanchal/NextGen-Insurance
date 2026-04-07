# 🛡️ Insurance Risk Insights Engine - Fintech Grade
A production-grade fintech risk analytics platform that combines Machine Learning (ML), Natural Language Processing (NLP), and Anomaly Detection to proactively manage insurance fraud and calculate dynamic risk scores. 

## 🎯 Architecture
The service was completely refactored to prioritize system resilience, data isolation (preventing data leakage), speed, and maintainable configuration logic.

### 1. Unified RiskEngine (Pipeline)
Located in `src/risk_engine.py`, the core is a custom Pipeline wrapper class, `RiskEngine`, which trains completely isolated transformers and predictors:
- **ML Classifier**: A robust `RandomForestClassifier` coupled to a `ColumnTransformer` (via `OneHotEncoder` and `StandardScaler`). Feature mappings (`TargetGuidedEncoder`) are securely calibrated purely on the Training Split (`X_train`) effectively preventing the `claim_type -> mean claim_amount` global data leakage bug.
- **NLP Text Analyzer**: A custom `TfidfVectorizer` computes the text vagueness as a proxy for missing detail.
- **Anomaly Detector**: An `IsolationForest` to spot numeric anomalies.

The `RiskEngine` enforces a static configuration footprint and supports both:
- `fit(X, y)`
- `predict(X)` 
- `predict_features(X)`

### 2. High-Performance FastAPI Backend
Located in `api/main.py`, models are asynchronously loaded into global memory **ONCE** using `@app.on_event("startup")`. Predict API requests bypass reloading the artifact, providing real-time ultra-fast inferencing.

### 3. Professional Streamlit Dashboard
The analytics interface supports robust data exploration, plotting distributions, and drill-downs into automatically flagged anomalous claims using multiple layout tiers and filters. Data is cached locally via `@st.cache_data`.

### 4. Database-Backed Operations
Flat CSV workflows were refactored into a `SQLite` architecture to support high IO operations safely across API boundaries and rapid dashboards. Features a sample synthetic data generator in `src/data_generation.py`.

## 🛠️ Usage

### Installation 
```bash
pip install -r requirements.txt
```

### 1️⃣ Generate DB & Train Model
```bash
python src/data_generation.py  # Gen 5000 claims (DB setup)
python src/model_training.py # Train RiskEngine and persist an artifact into models/
```

### 2️⃣ Start FastAPI Backend
```bash
cd api
uvicorn main:app --reload
```
`POST -> http://localhost:8000/predict-risk`

### 3️⃣ Launch Fintech Dashboard
```bash
streamlit run app/streamlit_app.py
```
