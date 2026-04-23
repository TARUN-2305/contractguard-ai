# Data & Training Methodology

This document outlines the origins, processing pipelines, and machine learning training architectures utilized within the ContractGuard AI platform.

## 1. Datasets & Provenance

The system relies on three primary data streams, transitioning from purely synthetic logic-testing boundaries to real-world, highly imbalanced infrastructure data.

### A. Kaggle Road Construction Delay Survey (Real-World)
* **Source:** Extracted during Operation Data-Heist from a competitor repository (`https://github.com/thepavan1/ContractGuard-AI.git`).
* **Original Structure:** 144 survey rows capturing respondent ratings on various infrastructure delay categories (e.g., material shortages, land acquisition delays).
* **Processing (`02b_real_data_ingestion.py`):** The data was "melted" from a wide survey format into a long, transactional execution log. Features like `planned_duration_days`, `actual_duration_days`, and `contractor_past_delay_rate` were algorithmically engineered based on severity scores.
* **Final Volume:** Expanded into **6,287 transactional rows** (`execution_merged_real.csv`).
* **Characteristics:** Highly imbalanced toward failure. **77.9% of rows represent violations** (delays exceeding grace periods), making compliance the minority class.

### B. CUAD v1 (Legal Annotations)
* **Source:** Atticus Project's Contract Understanding Atticus Dataset (CUAD), acquired during Operation Data-Heist.
* **Volume:** 510 commercial legal contracts.
* **Usage:** Provides dense, unstructured legalese for stress-testing Module 1's FAISS/HuggingFace RAG pipeline, ensuring the Llama-3.3-70B model can extract hidden deadlines and liquidated damage clauses from adversarial formatting.

### C. Synthetic Execution Generator (V1 Baseline)
* **Source:** Programmatically generated via `notebooks/02_execution_data.py`.
* **Volume:** 4,497 task records distributed across 1,000 mock infrastructure projects.
* **Characteristics:** Built to test the deterministic rules extracted from the mock `nhai_sample.pdf`. It features a **21.5% violation rate** (where violations are the minority class) and features randomized weather constraints and penalty rates.

---

## 2. Machine Learning Training Architecture

The predictive core (Module 4) utilizes an XGBoost Classifier to output failure probability scores. The training approach was bifurcated to handle the differing statistical imbalances of our datasets.

### A. V2.0 Cloud-Training Pipeline (Real-World Data)
* **Environment:** Offloaded to Google Colab utilizing **NVIDIA T4 GPUs** (`04b_real_risk_predictor_colab.ipynb`) due to the computational overhead of processing 6,200+ rows with synthetic resampling.
* **Class Balancing:** Because the real-world Kaggle data flipped the expected distribution (Violations = 77.9%, Compliant = 22.1%), we deployed **SMOTE (Synthetic Minority Over-sampling Technique)**. This algorithm synthetically upsampled the minority (compliant) class to achieve a 50/50 balance, preventing the model from defaulting to predicting failure for every task.
* **Model:** GPU-accelerated XGBoost (`tree_method='hist'`, `device='cuda'`).
* **Explainability:** SHAP (SHapley Additive exPlanations) was integrated to provide feature-level transparency (e.g., proving that `contractor_past_delay_rate` was driving the failure prediction).

### B. V1.0 Local Pipeline (Synthetic Data)
* **Environment:** Local CPU execution (`04_risk_predictor.py`).
* **Class Balancing:** With a 21.5% minority violation rate, we abandoned complex density-based oversampling (ADASYN) which caused runtime crashes, and instead utilized algorithmic penalization. We calculated and applied a strict **`scale_pos_weight`** during XGBoost initialization to heavily penalize the model for missing actual violations.
* **Evaluation:** Met strict production Go/No-Go criteria:
    * **CV AUROC:** 0.823 ± 0.008
    * **Minority Class Recall:** 0.789 (exceeding the 0.75 requirement, ensuring critical delays are rarely missed).

## 3. Integration into the Platform
Once trained, the models are exported as JSON artifacts (`risk_predictor_v1.json` / `risk_predictor_v2.json`) and loaded directly into Streamlit's `@st.cache_data` memory. As the Project Manager views active tasks, the model runs `predict_proba()` instantly across the dataframe, converting raw features into the sorted "Risk Score" column in the dashboard.
