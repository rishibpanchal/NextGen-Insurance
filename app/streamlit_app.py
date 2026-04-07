import streamlit as st
import pandas as pd
import requests
import json
import numpy as np
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_URL = "http://127.0.0.1:8000/predict-risk"

st.set_page_config(page_title="NexGen Risk Engine", layout="wide", initial_sidebar_state="expanded")

# --- UI HELPER: PREVENTS STREAMLIT FROM PARSING HTML AS MARKDOWN CODE BLOCKS ---
def ui(html_str):
    # Strip leading spaces from all lines so markdown engine ignores indentation
    clean_html = "\\n".join([line.lstrip() for line in html_str.split("\\n")])
    st.markdown(clean_html, unsafe_allow_html=True)

# ==============================================================================
# CSS OVERRIDES FOR SAAS FEEL + NATIVE WIDGET STYLING
# ==============================================================================
ui("""
<style>
/* Global Focus & Dark Theme */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0b0f19 !important;
    color: #e2e8f0;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 15% 50%, rgba(30, 41, 59, 1), rgba(15, 23, 42, 1) 25%, rgba(11, 15, 25, 1) 100%);
}
[data-testid="stHeader"] { background: rgba(11, 15, 25, 0.0); }
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.85);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(16px);
}
#MainMenu, footer {visibility: hidden;}

/* Custom Glassmorphism Containers */
.glass-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.2) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 24px;
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    margin-bottom: 24px;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px 0 rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    border-color: rgba(56, 189, 248, 0.3);
}

/* Base Typo */
.title-large { font-size: 2.25rem; font-weight: 700; color: #f8fafc; letter-spacing: -1px; margin-bottom: 4px; }
.title-medium { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; margin-bottom: 16px; letter-spacing: -0.5px;}
.kpi-value { font-size: 2.5rem; font-weight: 700; color: #f8fafc; letter-spacing: -1px; line-height: 1.2; }
.text-muted { font-size: 0.85rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;}
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; align-items:center; display:inline-flex; gap:6px;}

.badge-high { background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-medium { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-low { background-color: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }

.progress-container { width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; margin-top: 8px;}
.progress-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.progress-green { background: linear-gradient(90deg, #059669, #34d399); }
.progress-red { background: linear-gradient(90deg, #dc2626, #f87171); }
.progress-orange { background: linear-gradient(90deg, #d97706, #fbbf24); }

/* --- STYLING STREAMLIT NATIVE INPUTS --- */
div[role="radiogroup"] > label > div:first-child { display: none; }
div[role="radiogroup"] { gap: 4px; }
div[role="radiogroup"] > label { 
    padding: 10px 14px; border-radius: 10px; transition: background 0.2s; 
    font-weight: 500; font-size: 0.95rem; color: #cbd5e1; cursor: pointer;
}
div[role="radiogroup"] > label:hover { background: rgba(255,255,255,0.05); color: white;}
div[role="radiogroup"] > label[data-checked="true"] { 
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.1) 0%, transparent 100%); 
    border-left: 2px solid #38bdf8; color: #38bdf8; font-weight: 600; 
}

.stTextInput > div > div > input, .stSelectbox > div > div > div, .stNumberInput > div > div > input, .stTextArea > div > div > textarea { 
    background-color: rgba(255,255,255,0.05) !important; 
    color: white !important; 
    border: 1px solid rgba(255,255,255,0.1) !important; 
    border-radius: 8px !important; 
}
div.stButton > button:first-child[kind="primary"] {
    background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); color: white; border: none; border-radius: 10px;
    padding: 12px 24px; box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39); font-weight: 600; transition: all 0.2s;
}
div.stButton > button:first-child[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.23); transform: translateY(-2px);
    background: linear-gradient(135deg, #7dd3fc 0%, #3b82f6 100%);
}
div.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #e2e8f0 !important;
    border-radius: 8px !important; width: 100%; transition: all 0.2s; padding: 8px !important;
}
div.stDownloadButton > button:hover { background: rgba(56, 189, 248, 0.1) !important; border-color: rgba(56, 189, 248, 0.3) !important; color: #38bdf8 !important; }

/* Grid Table */
.data-table-header { display: grid; grid-template-columns: 1fr 2fr 1fr 1fr 1.5fr 1.5fr; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;}
.data-table-row { display: grid; grid-template-columns: 1fr 2fr 1fr 1fr 1.5fr 1.5fr; padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.03); align-items: center; font-size: 0.9rem; transition: background 0.2s;}
.data-table-row:hover { background: rgba(255,255,255,0.02); }
.data-table-row:last-child { border-bottom: none; }
</style>
""")

# ==============================================================================
# DATA PIPELINE
# ==============================================================================
@st.cache_data
def get_claims_data():
    csv_path = BASE_DIR / "data" / "processed" / "fully_scored_claims.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame()
        
    names = ["Eleanor Shellstrop", "Tahani Al-Jamil", "Chidi Anagonye", "Jason Mendoza", "Michael Realman", "Janet Snakehole", "Doug Forcett", "Mindy St. Claire"]
    np.random.seed(101)
    
    if len(df) > 0:
        df['holder_name'] = [names[i % len(names)] for i in range(len(df))]
        df['coverage_percent'] = np.random.randint(15, 99, size=len(df))
        df['risk_score'] = df['final_risk_score'].fillna(0.0) if 'final_risk_score' in df.columns else df.get('risk_score', np.random.rand(len(df)))
    return df

base_df = get_claims_data()

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    ui("""
        <div style="padding: 10px 0 20px 10px;">
            <div style="font-weight: 800; font-size: 1.5rem; color: white; display: flex; align-items: center; gap: 8px;">
                <div style="background: linear-gradient(135deg, #38bdf8, #3b82f6); width: 24px; height: 24px; border-radius: 6px; box-shadow: 0 0 15px rgba(56,189,248,0.5);"></div>
                NexGen Risk
            </div>
            <div style="font-size: 0.65rem; color: #64748b; letter-spacing: 1.5px; margin-top: 4px;">ANALYTICS ENGINE</div>
        </div>
        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700; letter-spacing: 1px; margin: 12px 0 0px 12px;">DASHBOARD</div>
    """)
    
    page = st.radio("Navigation", [
        "📊 Executive Overview", 
        "🔍 Live API Simulator", 
        "📋 Full Database Ledger"
    ], label_visibility="collapsed")
    
    ui("""
        <div style="font-size: 0.7rem; color: #64748b; font-weight: 700; letter-spacing: 1px; margin: 24px 0 8px 12px;">PREFERENCES</div>
        <div style="padding: 10px 14px; font-weight: 500; font-size: 0.95rem; color: #cbd5e1; cursor: pointer;">⚙️ Organization</div>
        <div style="padding: 10px 14px; font-weight: 500; font-size: 0.95rem; color: #cbd5e1; cursor: pointer;">❓ Docs & Help</div>
    """)

# ==============================================================================
# TOP BAR FILTERING
# ==============================================================================
col_title, col_search, col_filter, col_dl = st.columns([2.5, 1.5, 1, 1])

with col_title:
    title_map = {
        "📊 Executive Overview": "Risk Analytics",
        "🔍 Live API Simulator": "Neural Engine Prediction",
        "📋 Full Database Ledger": "Claims Database"
    }
    ui(f'<div class="title-large">{title_map[page]}</div>')

with col_search:
    search_query = st.text_input("Search", placeholder="🔍 Search IDs, Names, Policies...", label_visibility="collapsed")
with col_filter:
    risk_filter = st.selectbox("Risk Level", ["All Risks", "High", "Medium", "Low"], label_visibility="collapsed")
with col_dl:
    csv = base_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export CSV",
        data=csv,
        file_name="risk_report.csv",
        mime="text/csv",
    )

ui('<div class="text-muted" style="margin-bottom: 24px; text-transform:none;">Evaluate and manage anomalies via secure inference engine.</div>')

# DYNAMIC FILTERS
filtered_df = base_df.copy()
if search_query and len(filtered_df) > 0:
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
if risk_filter != "All Risks" and len(filtered_df) > 0:
    filtered_df = filtered_df[filtered_df['risk_category'] == risk_filter]


# ==============================================================================
# VIEW 1: EXECUTIVE OVERVIEW
# ==============================================================================
if page == "📊 Executive Overview":
    
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)

    total_exposed = filtered_df['claim_amount'].sum() if len(filtered_df) > 0 else 0
    high_risk_n = len(filtered_df[filtered_df['risk_category'] == 'High']) if len(filtered_df)>0 else 0
    anom_count = filtered_df['anomaly_flag'].sum() if len(filtered_df)>0 else 0

    with kpi_c1:
        ui(f"""
        <div class="glass-card" style="border-left: 2px solid #10b981; height: 90%;">
            <div class="text-muted">Total Coverge Exposure</div>
            <div class="kpi-value" style="color: #38bdf8; font-size: 2.1rem; margin-top:8px;">${total_exposed:,.0f}</div>
            <div style="margin-top: 8px; display:flex; gap: 8px;">
                <span style="background:rgba(16,185,129,0.2); color:#10b981; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600;">(Filtered Data)</span>
            </div>
        </div>
        """)

    with kpi_c2:
        ui(f"""
        <div class="glass-card" style="height: 90%;">
            <div class="text-muted">Avg Settlement Amount</div>
            <div class="kpi-value" style="font-size: 2.1rem; margin-top:8px;">${filtered_df['claim_amount'].mean() if len(filtered_df)>0 else 0:,.0f}</div>
        </div>
        """)

    with kpi_c3:
        ui(f"""
        <div class="glass-card" style="border-left: 2px solid #ef4444; height: 90%;">
            <div class="text-muted" style="color: #ef4444;">High Risk Identified</div>
            <div class="kpi-value" style="font-size: 2.1rem; margin-top:8px;">{high_risk_n}</div>
            <div style="margin-top: 8px; font-size:0.7rem; color:#94a3b8;">Threat vectors detected</div>
        </div>
        """)

    with kpi_c4:
        ui(f"""
        <div class="glass-card" style="border-left: 2px solid #f59e0b; height: 90%;">
            <div class="text-muted" style="color: #f59e0b;">ML Anomalies Flaged</div>
            <div class="kpi-value" style="font-size: 2.1rem; margin-top:8px;">{anom_count}</div>
            <div style="margin-top: 8px; font-size:0.7rem; color:#94a3b8;">Statistical isolates</div>
        </div>
        """)

    main_col, side_col = st.columns([1.8, 1])

    with main_col:
        ui('<div class="glass-card">')
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1: ui('<div class="title-medium">Top Priority Cases (Dynamic)</div>')
        
        history_headers = """
        <div class="data-table-header"><div>ID</div><div>POLICY HOLDER</div><div>TYPE</div><div>AMOUNT</div><div>VULNERABILITY</div><div>COVERAGE</div></div>
        """
        
        view_df = filtered_df.sort_values(by='risk_score', ascending=False).head(5) if len(filtered_df) > 0 else pd.DataFrame()
        rows_html = ""
        
        for _, row in view_df.iterrows():
            bag_col = "badge-high" if row['risk_category']=='High' else "badge-medium" if row['risk_category']=='Medium' else "badge-low"
            icon = "🔴" if row['risk_category']=='High' else "🟡" if row['risk_category']=='Medium' else "🟢"
            cov = row.get('coverage_percent', 50)
            p_class = "progress-red" if row['risk_category']=='High' else "progress-orange" if row['risk_category']=='Medium' else "progress-green"
            
            rows_html += f"""
            <div class="data-table-row">
                <div style="color:#64748b; font-family:monospace;">{row['claim_id']}</div>
                <div style="font-weight:500; display:flex; align-items:center; gap:8px;"><div style="background:#1e293b; width:24px; height:24px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:0.6rem;">{row['holder_name'][0]}</div>{row['holder_name']}</div>
                <div style="color:#94a3b8;">{row['claim_type']}</div>
                <div style="font-weight:600; color:#f1f5f9;">${float(row['claim_amount']):,.2f}</div>
                <div><span class="badge {bag_col}">{icon} {(row.get('risk_score', 0)*100):.1f}% Risk</span></div>
                <div style="padding-right:16px;"><div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#94a3b8; margin-bottom:4px;"><span>Utilized</span><span>{cov}%</span></div><div class="progress-container"><div class="progress-fill {p_class}" style="width: {cov}%;"></div></div></div>
            </div>
            """
            
        if len(view_df) == 0:
            rows_html = "<div style='padding:20px; color:#64748b;'>No claims match current filters.</div>"
            
        ui(history_headers + rows_html)
        ui('</div>')

    with side_col:
        ui('<div class="glass-card" style="height: 100%;">')
        ui('<div class="title-medium">Data Integrity Score</div>')
        
        base_health = 100 - (anom_count * 1.5) - (high_risk_n * 0.5)
        base_health = max(10.0, min(100.0, base_health))
        
        color_ring = "#10b981" if base_health > 80 else "#f59e0b" if base_health > 60 else "#ef4444"
        
        ui(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 20px 0;">
            <div style="width:140px; height:140px; border-radius:50%; background: radial-gradient(circle closest-side, transparent 80%, {color_ring} 110%); border: 8px solid rgba(255,255,255,0.02); display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:16px; box-shadow: 0 0 30px {color_ring}40;">
                <div style="font-size:2.5rem; font-weight:700; color:white; line-height:1;">{int(base_health)}%</div>
            </div>
            <div style="color:#94a3b8; font-size:0.85rem; max-width:200px; text-align:center;">
                 Overall portfolio safety based on active filter cohort.
            </div>
        </div>
        """)
        ui('</div>')

# ==============================================================================
# VIEW 2: LIVE API SIMULATOR
# ==============================================================================
elif page == "🔍 Live API Simulator":
    ui('<div class="glass-card">')
    ui('<div class="title-medium">Send Live Payload to Inference Engine</div>')
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        eval_id = st.text_input("Claim Tracking ID", placeholder="Ex: NX-491-00", value="CX-998A")
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            eval_type = st.selectbox("Policy Category", ["Auto", "Medical", "Home", "Travel"])
            eval_freq = st.number_input("Claim Frequency / Year", value=1)
        with col_inp2:
            eval_amt = st.number_input("Requested Settlement ($)", min_value=1.0, value=8500.50, step=500.0)
            eval_age = st.number_input("Holder Age", value=32)
            
        eval_desc = st.text_area("Adjuster Intake Narrative", "Customer repeatedly altering timeline facts. States items lost while commuting abroad.", height=150)
        
        btn = st.button("Evaluate with Neural Engine", type="primary")

    with c2:
        if btn:
            payload = {
                "claim_id": eval_id or "TEST-01",
                "customer_id": "CUST-X",
                "claim_amount": float(eval_amt),
                "claim_type": eval_type,
                "claim_date": "2026-04-08",
                "customer_age": int(eval_age),
                "location": "NY",
                "claim_description": eval_desc,
                "past_claims": int(eval_freq),
                "claim_frequency": int(eval_freq)
            }
            
            try:
                with st.spinner("Connecting to Localhost API..."):
                    resp = requests.post(API_URL, json=payload, timeout=5.0)
                    
                if resp.status_code == 200:
                    res = resp.json()
                    
                    cat = res['risk_category']
                    if cat == 'High':
                        tag_col, b_col, icon = "#ef4444", "rgba(239,68,68,0.1)", "🚨"
                    elif cat == 'Medium':
                        tag_col, b_col, icon = "#f59e0b", "rgba(245,158,11,0.1)", "⚠️"
                    else:
                        tag_col, b_col, icon = "#10b981", "rgba(16,185,129,0.1)", "✅"
                    
                    features_html = ""
                    for drv in res['top_drivers'][:4]:
                        features_html += f"""
                        <div style="background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:6px; display:flex; justify-content:space-between; margin-bottom:6px; font-size:0.85rem; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="color:#94a3b8; font-family:monospace;">{drv['feature']}</span>
                            <span style="color:white; font-weight:600;">Weight: {drv['importance']:.4f}</span>
                        </div>
                        """
                        
                    anom_html = f"<span style='color:#ef4444; font-weight:600;'>🚨 Mathematical Outlier Flagged</span>" if res['anomaly_flag'] else f"<span style='color:#10b981; font-weight:600;'>✅ Normal Distribution Segment</span>"
                    
                    ui(f"""
                    <div style="background:{b_col}; border: 1px solid {tag_col}40; border-radius: 12px; padding: 24px; box-shadow: 0 10px 30px {tag_col}10;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="color:{tag_col}; font-weight:700; font-size:1.4rem; display:flex; align-items:center; gap:8px;">
                                    {icon} {cat} Priority Trajectory
                                </div>
                                <div style="color:#e2e8f0; font-size:0.9rem; margin-top:8px;">
                                    {res['explanation']}
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div class="kpi-value" style="font-size:2.4rem; color:white;">{res['risk_score']*100:.1f}%</div>
                                <div class="text-muted" style="font-size:0.7rem;">Confidence Aggregate</div>
                            </div>
                        </div>
                        
                        <div style="display:grid; grid-template-columns: 1fr 1.2fr; gap: 24px; margin-top: 24px;">
                            <div>
                                <div class="text-muted" style="font-size:0.75rem; margin-bottom:8px;">Statistical Boundaries</div>
                                <div style="background:rgba(255,255,255,0.03); padding:16px; border-radius:8px; font-size:0.85rem; border-left:2px solid {tag_col};">
                                    {anom_html}
                                </div>
                            </div>
                            <div>
                                <div class="text-muted" style="font-size:0.75rem; margin-bottom:8px;">Decisive ML Tensors</div>
                                {features_html}
                            </div>
                        </div>
                    </div>
                    """)
                else:
                    st.error(f"API Engine Fault {resp.status_code}: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("API Bridge Refused! Ensure Uvicorn (FastAPI) is running at http://127.0.0.1:8000.")
        else:
            st.info("👈 Enter claim details on the left and click 'Evaluate' to ping the local AI engine.")
            
    ui('</div>')

# ==============================================================================
# VIEW 3: FULL DATABASE LEDGER
# ==============================================================================
elif page == "📋 Full Database Ledger":
    ui('<div class="glass-card" style="padding-bottom: 0px;">')
    ui('<div class="title-medium">Interactive Deep Dive</div>')
    ui('<div class="text-muted" style="margin-bottom:16px; text-transform:none;">Explore, sort, and analyze the raw structured dataframe directly in the browser.</div>')
    
    if len(filtered_df) > 0:
        # Configure columns to display cleanly via standard st.dataframe config features
        show_df = filtered_df[['claim_id', 'holder_name', 'claim_type', 'claim_amount', 'risk_category', 'anomaly_flag', 'final_risk_score', 'claim_description']].copy()
        
        st.dataframe(
            show_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "claim_id": "Claim ID",
                "holder_name": "Policy Holder",
                "claim_type": "Category",
                "claim_amount": st.column_config.NumberColumn("Amount Raised", format="$%.2f"),
                "risk_category": "AI Priority",
                "anomaly_flag": "Anomaly",
                "final_risk_score": st.column_config.ProgressColumn("Threat Score", format="%.2f", min_value=0.0, max_value=1.0),
                "claim_description": "NLP Notes"
            },
            height=600
        )
    else:
        st.warning("No data satisfies current search/filter conditions.")
        
    ui('</div>')