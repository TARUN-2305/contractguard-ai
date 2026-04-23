# ContractGuard AI — Core Architecture & Real-World Application Guide

## Component 1: The AI Legal Reader (Module 1)
* **File References:** `notebooks/01_contract_parser.py`, `data/raw_contracts/`, `data/rule_store/contract_001_rules.json`
* **Persona:** Contract Manager (`app/app.py`)
* **Concept:** Automated RAG pipeline for extracting rules from unstructured PDF text.

The AI Legal Reader leverages a Retrieval-Augmented Generation (RAG) architecture powered by FAISS vector stores and the Groq Llama-3.3-70B model to intelligently ingest raw legal PDF documents and extract highly structured rule sets.

**Real-World Examples:**
1. **Finding Hidden Deadlines:** Automatically scraping dense legalese to pinpoint the exact 60-day completion deadline for bridge deck construction.
2. **Identifying Grace Periods:** Uncovering stipulated extension buffers, such as a 5-day grace period allocated for weather disruptions.
3. **Extracting Exact Financial Liquidated Damages:** Isolating complex financial penalties, ensuring a rate of exactly ₹15,000/day is recorded for specific delayed tasks.
4. **Adapting Dynamically to Formats:** Seamlessly parsing wildly different contract structures, whether it's a standard NHAI agreement or a complex international FIDIC format.
5. **Retaining Clause Citations:** Maintaining the exact legal reference within the contract text for robust, unassailable audit trails.

## Component 2: The Ground-Level Tracker (Module 3)
* **File References:** `notebooks/03_compliance_engine.py`, `data/execution_merged_real.csv`
* **Persona:** Site Engineer (`app/app.py`)
* **Concept:** Deterministic matching engine that compares field logs against Llama-3.3-extracted rules.

The Ground-Level Tracker serves as the deterministic logic core of the platform. It algorithmically enforces compliance by cross-referencing live, on-the-ground execution reports directly against the structured rules extracted by Module 1.

**Real-World Examples:**
1. **Calculating Precise Violations:** Instantly mapping a field report indicating 75 days against a 60-day deadline, netting a 10-day violation after applying the 5-day contractual grace period.
2. **Recalculating for Weather:** Dynamically adjusting the compliance status based on legitimate site engineer inputs, such as active monsoon weather flags.
3. **Instantly Billing the Ledger:** Mathematically multiplying the final delayed days by the exact extracted penalty rate to generate immediate ledger adjustments without manual intervention.
4. **Clearing Compliant Work:** Autonomously validating successful, on-time task completions, triggering rapid sign-offs for fast contractor payment releases.
5. **Eliminating Human Error:** Removing the risk of human oversight by digitally enforcing contract thresholds that are easily forgotten across multi-year infrastructure lifecycles.

## Component 3: The Risk Predictor (Module 4)
* **File References:** `notebooks/04_risk_predictor.py`, `notebooks/04b_real_risk_predictor_colab.ipynb`, `data/models/risk_predictor_v1.json`
* **Persona:** Project Manager (`app/app.py`)
* **Concept:** XGBoost Machine Learning model trained on Kaggle survey data to output predictive failure probabilities.

The Risk Predictor transforms the system from reactive to proactive. Utilizing an XGBoost classifier balanced with SMOTE (or ADASYN), it analyzes thousands of real-world Indian road construction data points to assign a highly accurate failure probability score to live project tasks.

**Real-World Examples:**
1. **Flagging Subcontractor History:** Elevating the risk score on an upcoming excavation task because the assigned subcontractor holds a historical 40% failure rate.
2. **Mapping the Cascade Effect:** Identifying how a 3-day delay in utility shifting exponentially spikes the mathematical risk of failure for the subsequent sub-base course preparation.
3. **Applying Weather Risk Multipliers:** Proactively warning project managers of elevated delay probabilities when scheduling sensitive tasks like paving during the peak monsoon season.
4. **Intelligent Dashboard Sorting:** Empowering Project Managers to sort an overwhelming 50-task dashboard not by alphabetical order, but purely by descending ML risk scores.
5. **Enabling Proactive Intervention:** Triggering early-warning alerts that allow project managers to call vendor intervention meetings at Day 15, well before a Day 61 disaster occurs.

## Component 4: The Explainer & Agent Layer (Modules 5 & 6)
* **File References:** `notebooks/05_agent.py`, `notebooks/06_explainer.py`
* **Personas:** Auditor, Contractor Rep (`app/app.py`)
* **Concept:** Rule-based agent triggering downstream actions and Groq LLM synthesizing plain-English justifications.

The final layer bridges the gap between raw data and human decision-making. Module 5 acts as an autonomous routing agent, while Module 6 utilizes the Groq LLM to translate complex contractual and mathematical outputs into digestible, highly readable intelligence.

**Real-World Examples:**
1. **Executive Summary Generation:** Drafting an executive briefing that clearly states the exact delays and financial damages in under 100 words, stripped of confusing technical jargon.
2. **Automated Audit Compilations:** Generating robust, professional PDF reports via `fpdf2` for direct submission to government inspectors or independent auditors.
3. **Transparent Dispute Logging:** Allowing contractors to log formal dispute reasons directly against the automated fines, preserving an immutable record of contention.
4. **Acting as an Impartial Referee:** Operating as a cold, text-based intermediary, resolving disputes based entirely on extracted text and math rather than heated, emotional arguments.
5. **CEO-Ready Intelligence:** Providing high-level, non-technical stakeholders with immediately readable summaries, shielding them from raw AUROC metrics or dense JSON payloads.
