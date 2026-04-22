# ContractGuard AI

**Summary:** An autonomous, multi-agent framework designed to parse infrastructure contracts (NHAI/FIDIC), extract compliance rules via RAG (Llama 3.3 70B), and predict execution risks using XGBoost. Built entirely on a free-tier stack, it translates complex legal and operational data into plain-English decisions for multi-persona stakeholders.

## Key Features & Tasks

* **Automated Extraction:** Converts unstructured PDF concession agreements into structured JSON compliance rules.
* **Execution Matching:** Cross-references daily site logs against extracted rules to calculate grace periods and financial penalties.
* **Risk Prediction:** Predicts the probability of upcoming task delays based on historical contractor data, monsoon presence, and task sequences.
* **Agentic Decision Engine:** LLM-powered logic layer that escalates high-risk tasks and generates non-technical explanations for auditors and managers.

## I/O & Data Schema

* **Inputs:** Contract PDFs (Unstructured text), Daily Execution Logs (CSV format: `task_id`, `actual_duration_days`, `contractor_past_delay_rate`, etc.).
* **Outputs:** Extracted Rules (JSON), Risk Scores (Float `0.0 - 1.0`), Plain-English Explanations (String), Multi-persona Streamlit Dashboard.

## Setup & Execution

1. Clone the repository to your local machine.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to create a `.env` file and configure it with your `GROQ_API_KEY`:
   ```bash
   cp .env.example .env
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app/app.py
   ```
