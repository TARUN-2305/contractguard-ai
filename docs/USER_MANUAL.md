# ContractGuard AI — User Manual

Welcome to the ContractGuard AI interface. This multi-persona platform bridges the gap between raw legal stipulations and active construction execution. 

---

## 1. Contract Manager
**Role:** Initializes the system and sets the legal parameters.
**Workflow:** Uploads NHAI or FIDIC contract PDFs. The system automatically parses the legal text and extracts compliance boundaries (grace periods, penalty thresholds, deadlines) into the active Rule Store.

![Contract Manager View](/C:/Users/tarun/.gemini/antigravity/scratch/contractguard/docs/assets/screenshot_contract_manager.png)

---

## 2. Project Manager
**Role:** High-level supervision and financial risk mitigation.
**Workflow:** Tracks total active violations and accumulated penalty amounts in real-time. Reviews predicted high-risk delays flagged by the ML model.

![Project Manager View](/C:/Users/tarun/.gemini/antigravity/scratch/contractguard/docs/assets/screenshot_project_manager.png)

---

## 3. Site Engineer
**Role:** Ground-level execution logging.
**Workflow:** Selects the active task and inputs actual days taken. Flags weather conditions (e.g., monsoon) for real-time compliance recalibration against the baseline rule.

![Site Engineer View](/C:/Users/tarun/.gemini/antigravity/scratch/contractguard/docs/assets/screenshot_site_engineer.png)

---

## 4. Auditor
**Role:** External compliance review and reporting.
**Workflow:** Analyzes unfiltered tabular data of all confirmed violations. Capable of exporting comprehensive audit reports directly from the system for statutory compliance checking.

![Auditor View](/C:/Users/tarun/.gemini/antigravity/scratch/contractguard/docs/assets/screenshot_auditor.png)

---

## 5. Contractor Rep
**Role:** Third-party vendor accountability tracking.
**Workflow:** Reviews financial penalties actively levied against their firm. Features a direct portal to log dispute reasons against automated penalty triggers.

![Contractor Rep View](/C:/Users/tarun/.gemini/antigravity/scratch/contractguard/docs/assets/screenshot_contractor_rep.png)

---

### Troubleshooting & FAQ

*   **Q: Why isn't the PDF rule extraction working?**
    *   **A:** Ensure your `.env` file correctly contains your active `GROQ_API_KEY`. Without it, the Llama model cannot parse the RAG vectorstore.
*   **Q: The Risk predictions seem inaccurate.**
    *   **A:** The XGBoost model dynamically weights contractor history. If the contractor is new, the system assumes a baseline probabilistic risk. Let the execution data accumulate to stabilize predictions.
*   **Q: The UI crashed or shows a blank page.**
    *   **A:** Verify that the backend port 8501 is completely free and that the local `execution_merged.csv` has not been manually edited with corrupted schema headers.
