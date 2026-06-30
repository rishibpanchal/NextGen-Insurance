# 🛡️ Insurance Risk Insights Engine - Fintech Grade Platform

A production-grade fintech risk analytics and compliance platform built to proactively manage insurance fraud, enforce data privacy, and calculate dynamic risk scores. This platform demonstrates advanced capabilities in Machine Learning (ML), Natural Language Processing (NLP), and Full-Stack Engineering.

## 🎯 Core Product Offerings

This platform was specifically engineered to emulate enterprise-grade FinTech compliance tools:

### 1. **Data Privacy & Redaction Vault**
Built with data protection regulations (like the DPDP Act) in mind. The system features a strict NLP pre-processing module (`api/pii_redactor.py`) that instantly scrubs Personally Identifiable Information (PII)—including National IDs, Tax IDs, Phone Numbers, and Emails—from adjuster narratives *before* the AI processes the text.

### 2. **e-KYC & AML Gateway**
The system incorporates hard business-logic routing to override Machine Learning models. If an applicant fails standard e-KYC checks, the engine intercepts the claim, bypasses the ML probability, forces an AML (Anti-Money Laundering) flag, and routes the claim directly to Special Investigation Unit (SIU) Fraud Investigators.

### 3. **Batch Auto-Adjudication (STP)**
Features a highly-scalable "Batch Adjudication" module. Users can drag and drop raw CSV data files containing hundreds of claims. The system runs bulk inference using Pandas and XGBoost to instantly triage claims into Auto-Approved (Straight-Through Processing), Manual Review, or SIU Routing.

## 🏗️ Architecture Stack

### Backend & ML Pipeline
*   **FastAPI**: High-performance asynchronous REST API (`api/main.py`).
*   **XGBoost & Scikit-Learn**: The core `RiskEngine` uses `XGBClassifier` for robust structured data prediction and SHAP for explainable AI.
*   **Sentence Transformers (NLP)**: Replaced basic TF-IDF with `all-MiniLM-L6-v2` embeddings for deep semantic analysis of adjuster claim descriptions.
*   **SQLAlchemy & SQLite**: Fully migrated from flat CSVs to an ORM-backed relational database structure (`data/insurance_risk.db`) for rapid transactional queries and safe data fetching.

### Frontend Platform
*   **Next.js 14 & React**: A lightning-fast, App Router-based frontend.
*   **Tailwind CSS (Neumorphic Design)**: Features a premium, custom Neumorphic UI design system with smooth micro-animations and a unified color palette.
*   **Recharts**: High-performance interactive SVG charting.

## 🧭 Key Features
*   **Executive Dashboard**: Real-time KPIs, exposure charts, and portfolio data integrity scores.
*   **Live API Simulator**: An interactive playground to ping the AI engine with synthetic data. Features live SHAP tensor visualization to explain *why* the AI made its decision.
*   **Batch Triage**: Drag-and-drop CSV bulk processing.
*   **Individual Claim Analyzer**: A dedicated deep-dive view for specific claims. Includes historical ML/NLP score tracking and single-claim CSV exports.

## 🛠️ Local Development & Usage

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
uv sync
```

### 2. Start the Backend API (Port 8000)
```bash
# Start the FastAPI server with hot-reloading
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start the Frontend Platform (Port 3000)
```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev
```

The platform will be available at [http://localhost:3000](http://localhost:3000).
