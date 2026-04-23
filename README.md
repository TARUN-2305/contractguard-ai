# ContractGuard AI

**Total Summary:** An autonomous, multi-agent framework designed to parse infrastructure contracts (NHAI/FIDIC), extract compliance rules via RAG (Llama 3.3 70B), and predict execution risks using XGBoost. Built entirely on a free-tier stack, it translates complex legal and operational data into plain-English decisions for multi-persona stakeholders.

## Key Features & Tasks

*   **Automated Extraction:** Converts unstructured PDF concession agreements into structured JSON compliance rules.
*   **Execution Matching:** Cross-references daily site logs against extracted rules to calculate grace periods and financial penalties.
*   **Risk Prediction:** Predicts the probability of upcoming task delays based on historical contractor data, weather patterns, and task sequences.
*   **Agentic Decision Engine:** LLM-powered logic layer that escalates high-risk tasks and generates non-technical explanations for auditors.

## I/O, Formats, & Data Schema

*   **Inputs:** Contract PDFs (Unstructured text), Daily Execution Logs (CSV format: `task_id`, `actual_duration_days`, `contractor_past_delay_rate`, `is_monsoon_period`).
*   **Outputs:** Extracted Rules (JSON), Risk Scores (Float `0.0 - 1.0`), Plain-English Explanations (String), Multi-persona Streamlit Dashboard.

## Setup & Execution

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/TARUN-2305/contractguard-ai.git
    cd contractguard-ai
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file in the root directory and add your Groq API Key:
    ```text
    GROQ_API_KEY=your_api_key_here
    ```

4.  **Launch the UI:**
    ```bash
    streamlit run app/app.py
    ```
