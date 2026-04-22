import os
import json
from groq import Groq
from dotenv import load_dotenv

def generate_explanation(violation_record, agent_decisions):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    EXPLANATION_PROMPT = """
You are a construction contract compliance officer. Write a clear, plain-English explanation
of the following contract violation for a project manager or government auditor.
Include: what happened, which clause was violated, the financial consequence, and one recommendation.
Keep it strictly under 100 words.

VIOLATION DATA:
{violation_json}

AGENT DECISIONS:
{decisions_json}

Write the explanation now:
"""
    prompt = EXPLANATION_PROMPT.replace("{violation_json}", json.dumps(violation_record, indent=2))
    prompt = prompt.replace("{decisions_json}", json.dumps(agent_decisions, indent=2))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Testing Module 6: Explainer...")
    sample_violation = {
        "task_type": "bridge_deck_construction",
        "violation": True,
        "overrun_days": 12,
        "grace_period_days": 5,
        "penalty_inr": 105000,
        "contractor_past_delay_rate": 0.45,
        "clause_ref": "Unknown/Rule 3"
    }

    decisions = [
        {"action": "TRIGGER_PENALTY", "amount_inr": 105000, "reason": "Exceeded grace."},
        {"action": "ALERT_PROJECT_MANAGER", "risk_score": 0.81},
        {"action": "ESCALATE_TO_AUDITOR", "reason": "High historical delay."}
    ]
    
    explanation = generate_explanation(sample_violation, decisions)
    word_count = len(explanation.split())
    
    explanation_safe = explanation.replace("\u20b9", "INR ")
    print(f"\n--- Output ({word_count} words) ---\n{explanation_safe}\n")
    
    if word_count < 100 and ("105000" in explanation or "105,000" in explanation):
        print("[SUCCESS] Explainer criteria met (<100 words, financial reference included).")
    else:
        print("[FAIL] Explanation did not meet constraints.")
        exit(1)
