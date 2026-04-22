import streamlit as st
import pandas as pd
import xgboost as xgb
import json
import os
from groq import Groq

st.set_page_config(page_title="ContractGuard AI", layout="wide")

# ── SIDEBAR ──────────────────────────────────────────────
st.sidebar.title("ContractGuard AI")
persona = st.sidebar.selectbox("Login as:", 
    ["Contract Manager", "Project Manager", "Site Engineer", "Auditor", "Contractor Rep"])

# ── LOAD DATA ────────────────────────────────────────────
@st.cache_data
def load_data():
    # Since streamlit run app/app.py is executed from root directory, 
    # the relative paths mapped to "data/" will resolve correctly.
    df = pd.read_csv("data/execution_merged.csv")
    model = xgb.XGBClassifier()
    model.load_model("data/models/risk_predictor_v1.json")
    return df, model

df, risk_model = load_data()

# ── CONTRACT MANAGER VIEW ─────────────────────────────────
if persona == "Contract Manager":
    st.title("Contract Manager — Upload & Setup")
    
    uploaded = st.file_uploader("Upload contract PDF", type="pdf")
    if uploaded:
        st.success("Contract received. Running AI extraction...")
        # Call Module 1 pipeline here
        st.json({"task": "bridge_deck_construction", "deadline_days": 60, "grace_days": 5, 
                 "penalty_per_day_inr": 15000})
        if st.button("Confirm rules and go live"):
            st.success("Project is live. Notifying team.")

# ── PROJECT MANAGER VIEW ──────────────────────────────────
elif persona == "Project Manager":
    st.title("Project Dashboard")
    
    col1, col2, col3 = st.columns(3)
    violations = df[df.violation == 1]
    col1.metric("Active violations", len(violations))
    col2.metric("Total penalty", f"₹{violations.penalty_amount_inr.sum():,.0f}")
    col3.metric("Compliance rate", f"{(1 - df.violation.mean()):.1%}")
    
    st.subheader("Violations")
    st.dataframe(violations[["task_type","delay_days","penalty_amount_inr",
                              "delay_cause"]].head(20))

# ── SITE ENGINEER VIEW ────────────────────────────────────
elif persona == "Site Engineer":
    st.title("Log Progress")
    
    task = st.selectbox("Task", ["bridge_deck_construction", "sub_base_course_preparation", "bituminous_macadam_laying"])
    actual_days = st.number_input("Actual days taken", min_value=1, max_value=365)
    monsoon = st.checkbox("Monsoon period?")
    
    if st.button("Submit"):
        st.success(f"Logged: {task} completed in {actual_days} days. Compliance check running...")

# ── AUDITOR VIEW ──────────────────────────────────────────
elif persona == "Auditor":
    st.title("Audit Reports")
    st.dataframe(df[df.violation == 1].head(50))
    
    if st.button("Generate PDF Report"):
        st.download_button("Download report", data="audit_report.pdf", 
                           file_name="audit_report.pdf")

# ── CONTRACTOR VIEW ───────────────────────────────────────
elif persona == "Contractor Rep":
    st.title("My Violations")
    my_violations = df[df.violation == 1].head(10)
    for _, row in my_violations.iterrows():
        with st.expander(f"{row['task_type']} — ₹{row['penalty_amount_inr']:,.0f}"):
            dispute = st.text_area("Dispute reason (optional)", key=f"dispute_{row['task_id']}")
            if st.button(f"Submit dispute for {row['task_id']}", key=f"btn_{row['task_id']}"):
                st.info("Dispute submitted. Project manager notified.")
