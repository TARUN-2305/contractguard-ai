import os
import json
import fitz  # pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # newer package
from groq import Groq
from dotenv import load_dotenv

def run_pipeline():
    print("Starting Module 1 Pipeline...")
    # Setup Groq
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("GROQ_API_KEY environment variable is missing.")
    client = Groq(api_key=api_key)

    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_contracts', 'nhai_sample.pdf')
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    print("Extracting text from PDF...")
    def extract_text_from_pdf(path):
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)

    contract_text = extract_text_from_pdf(pdf_path)

    print("Building Vector Store...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([contract_text])

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    vs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'vectorstore')
    os.makedirs(vs_dir, exist_ok=True)
    vectorstore.save_local(os.path.join(vs_dir, "nhai_sample"))
    print("Vector Store Saved.")

    FEW_SHOT_PROMPT = """
You are a construction contract analyst. Extract structured rules from the contract text below.
For each task found, extract: task name, deadline in days, grace period in days, penalty per day in INR, quality specification.

EXAMPLE INPUT:
"The contractor shall complete sub-base course preparation within 45 days of commencement.
A grace period of 5 days is permitted. Delays beyond grace period attract ₹15,000 per day penalty."

EXAMPLE OUTPUT:
{
  "tasks": [
    {
      "task_name": "sub_base_course_preparation",
      "deadline_days": 45,
      "grace_period_days": 5,
      "penalty_per_day_inr": 15000,
      "quality_spec": null
    }
  ]
}

Now extract from this contract text. Output ONLY valid JSON, no other text:

CONTRACT TEXT:
{contract_chunk}
"""

    def extract_rules_from_contract(vectorstore, query_terms, top_k=5):
        results = []
        for term in query_terms:
            docs = vectorstore.similarity_search(term, k=top_k)
            for doc in docs:
                prompt = FEW_SHOT_PROMPT.replace("{contract_chunk}", doc.page_content)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=1000
                )
                try:
                    # attempt to parse the JSON
                    raw_content = response.choices[0].message.content
                    # Sometimes there are trailing chars, or markdown. Strip markdown blocks if they exist:
                    if raw_content.startswith("```json"):
                        raw_content = raw_content[7:-3]
                    elif raw_content.startswith("```"):
                        raw_content = raw_content[3:-3]
                        
                    extracted = json.loads(raw_content.strip())
                    results.extend(extracted.get("tasks", []))
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from model response for term: {term}")
                    pass
        return results

    print("Running Groq extraction...")
    query_terms = ["deadline penalty days", "completion grace period", 
                   "liquidated damages", "time for completion", "damages for delay"]

    rules = extract_rules_from_contract(vectorstore, query_terms)
    
    # Simple deduplication based on task_name
    deduped_rules = []
    seen = set()
    for r in rules:
        if r.get("task_name") not in seen:
            deduped_rules.append(r)
            seen.add(r.get("task_name"))

    print("\nExtraction Complete. Found Rules:")
    print(json.dumps(deduped_rules, indent=2))
    
    rs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'rule_store')
    os.makedirs(rs_dir, exist_ok=True)
    with open(os.path.join(rs_dir, "contract_001_rules.json"), "w") as f:
        json.dump(deduped_rules, f, indent=2)

    return len(deduped_rules)

if __name__ == "__main__":
    count = run_pipeline()
    if count >= 5:
        print("[SUCCESS] Extracted >= 5 rules.")
    else:
        print(f"[FAIL] Only extracted {count} rules. Must be >= 5.")
        exit(1)
