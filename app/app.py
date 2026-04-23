import streamlit as st
import pandas as pd
import xgboost as xgb
import json
import os
import importlib
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from fpdf import FPDF

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamic imports for numbered modules
parser_mod = importlib.import_module("notebooks.01_contract_parser")
run_pipeline = parser_mod.run_pipeline

comp_mod = importlib.import_module("notebooks.03_compliance_engine")
check_compliance = comp_mod.check_compliance

agent_mod = importlib.import_module("notebooks.05_agent")
agent_decide = agent_mod.agent_decide

explainer_mod = importlib.import_module("notebooks.06_explainer")
generate_explanation = explainer_mod.generate_explanation

st.set_page_config(page_title="ContractGuard AI", layout="wide")

# ── SIDEBAR ──────────────────────────────────────────────
st.sidebar.title("ContractGuard AI")
persona = st.sidebar.selectbox("Login as:", 
    ["Contract Manager", "Project Manager", "Site Engineer", "Auditor", "Contractor Rep"])

# ── LOAD DATA ────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/execution_merged.csv")
    model = xgb.XGBClassifier()
    model.load_model("data/models/risk_predictor_v1.json")
    
    # Load rules for site engineer
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rule_store', 'contract_001_rules.json')
    try:
        with open(rules_path, 'r') as f:
            rules = json.load(f)
        rule_lookup = {r['task_name']: r for r in rules}
    except:
        rule_lookup = {}
        
    return df, model, rule_lookup

df, risk_model, rule_lookup = load_data()

# ── CONTRACT MANAGER VIEW ─────────────────────────────────
if persona == "Contract Manager":
    st.title("Contract Manager — Upload & Setup")
    
    uploaded = st.file_uploader("Upload contract PDF", type="pdf")
    if uploaded:
        st.success("Contract received. Running AI extraction...")
        with st.spinner('Extracting rules via LLM & RAG...'):
            rules_extracted = run_pipeline(pdf_stream=uploaded.read())
            st.dataframe(pd.DataFrame(rules_extracted))
        
        if st.button("Confirm rules and go live"):
            st.success("Project is live. Notifying team.")

# ── PROJECT MANAGER VIEW ──────────────────────────────────
elif persona == "Project Manager":
    st.title("Project Dashboard")
    
    col1, col2, col3 = st.columns(3)
    violations = df[df.violation == 1].copy()
    col1.metric("Active violations", len(violations))
    col2.metric("Total penalty", f"₹{violations.penalty_amount_inr.sum():,.0f}")
    col3.metric("Compliance rate", f"{(1 - df.violation.mean()):.1%}")
    
    st.subheader("Violations & Risk Prediction")
    
    features = ['planned_duration_days', 'grace_period_days', 'contractor_past_delay_rate', 
                'is_monsoon_period', 'material_supply_delay', 
                'preceding_task_delayed', 'task_sequence_index', 'penalty_per_day_inr']
    
    if len(violations) > 0 and all(f in violations.columns for f in features):
        probs = risk_model.predict_proba(violations[features])[:, 1]
        violations["Risk Score"] = probs
        violations = violations.sort_values("Risk Score", ascending=False)
        st.dataframe(violations[["task_type","delay_days","penalty_amount_inr", "delay_cause", "Risk Score"]].head(20))
    else:
        st.dataframe(violations[["task_type","delay_days","penalty_amount_inr", "delay_cause"]].head(20))

# ── SITE ENGINEER VIEW ────────────────────────────────────
elif persona == "Site Engineer":
    st.title("Log Progress")
    
    task = st.selectbox("Task", ["bridge_deck_construction", "sub_base_course_preparation", "bituminous_macadam_laying", "site_clearance_and_excavation", "guardrail_installation"])
    actual_days = st.number_input("Actual days taken", min_value=1, max_value=365)
    monsoon = st.checkbox("Monsoon period?")
    
    if st.button("Submit"):
        st.success(f"Logged: {task} completed in {actual_days} days. Compliance check running...")
        
        execution_row = {
            "task_type": task,
            "actual_duration_days": actual_days
        }
        
        result = check_compliance(execution_row, rule_lookup)
        
        if result["status"] == "compliant" or result["status"] == "within_grace":
            st.info(f"✅ COMPLIANT. Overrun: {result['overrun_days']} days.")
            agent_record = {"violation": False, "penalty_inr": 0}
        else:
            st.error(f"❌ VIOLATION! Penalty: ₹{result['penalty_pred']:,.0f}")
            agent_record = {
                "violation": True, 
                "penalty_inr": result["penalty_pred"], 
                "overrun_days": result["overrun_days"], 
                "grace_period_days": rule_lookup.get(task, {}).get("grace_period_days", 0),
                "contractor_past_delay_rate": 0.5
            }
            
        decisions = agent_decide(agent_record, risk_score=0.5)
        st.write("Agent Decisions:")
        st.json(decisions)

# ── AUDITOR VIEW ──────────────────────────────────────────
elif persona == "Auditor":
    st.title("Audit Reports")
    st.dataframe(df[df.violation == 1].head(50))
    
    if st.button("Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        pdf.cell(200, 10, text="ContractGuard AI Audit Report", new_x="LMARGIN", new_y="NEXT", align='C')
        
        violations_head = df[df.violation == 1].head(10)
        for _, row in violations_head.iterrows():
            pdf.cell(200, 10, text=f"Task: {row['task_type']} | Delay: {row['delay_days']} days | Penalty: INR {row['penalty_amount_inr']}", new_x="LMARGIN", new_y="NEXT")
            
        pdf_bytes = pdf.output()
        st.download_button("Download report", data=bytes(pdf_bytes), 
                           file_name="audit_report.pdf", mime="application/pdf")

# ── CONTRACTOR VIEW ───────────────────────────────────────
elif persona == "Contractor Rep":
    st.title("My Violations")
    my_violations = df[df.violation == 1].head(10)
    for _, row in my_violations.iterrows():
        with st.expander(f"{row['task_type']} — ₹{row['penalty_amount_inr']:,.0f}"):
            if st.button(f"Generate Explanation for {row['task_id']}"):
                with st.spinner("Agent generating explanation..."):
                    record = {
                        "task_type": row["task_type"],
                        "violation": True,
                        "overrun_days": row["delay_days"],
                        "grace_period_days": row.get("grace_period_days", 0),
                        "penalty_inr": row["penalty_amount_inr"],
                        "contractor_past_delay_rate": row.get("contractor_past_delay_rate", 0),
                        "clause_ref": "Unknown"
                    }
                    decisions = agent_decide(record, risk_score=0.8)
                    explanation = generate_explanation(record, decisions)
                    st.write(explanation)
                    
            dispute = st.text_area("Dispute reason (optional)", key=f"dispute_{row['task_id']}")
            if st.button(f"Submit dispute for {row['task_id']}", key=f"btn_{row['task_id']}"):
                st.info("Dispute submitted. Project manager notified.")
