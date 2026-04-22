import pandas as pd
import json
import os
from sklearn.metrics import precision_score, recall_score, f1_score

def check_compliance(execution_row, rule_lookup):
    task = execution_row["task_type"]
    rule = rule_lookup.get(task)
    
    if not rule:
        return {"status": "no_rule", "violation_pred": False, "penalty_pred": 0, "overrun_days": 0}
    
    actual = execution_row["actual_duration_days"]
    deadline = rule.get("deadline_days", 0)
    grace = rule.get("grace_period_days", 0) or 0
    penalty_rate = rule.get("penalty_per_day_inr", 0) or 0
    
    overrun = actual - deadline
    
    if overrun <= 0:
        return {"status": "compliant", "violation_pred": False, "penalty_pred": 0, "overrun_days": 0}
    elif overrun <= grace:
        return {"status": "within_grace", "violation_pred": False, "penalty_pred": 0, "overrun_days": overrun}
    else:
        penalty_days = overrun - grace
        penalty = penalty_days * penalty_rate
        return {
            "status": "violation",
            "violation_pred": True,
            "overrun_days": overrun,
            "penalty_days": penalty_days,
            "penalty_pred": penalty,
            "clause_ref": rule.get("clause_reference", "Unknown"),
        }

def run_compliance_engine():
    print("Starting Module 3 Compliance Engine...")
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'execution_merged.csv')
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rule_store', 'contract_001_rules.json')
    
    df = pd.read_csv(csv_path)
    with open(rules_path, 'r') as f:
        rules = json.load(f)
        
    rule_lookup = {r['task_name']: r for r in rules}
    print(f"Loaded {len(df)} execution records")
    print(f"Rule store: {len(rules)} rules bounded")

    # Apply Rules
    violations = df.apply(lambda row: check_compliance(row, rule_lookup), axis=1)
    results = pd.DataFrame(violations.tolist())
    
    # Calculate precision & recall against ground truth
    y_true = df["violation"].values
    y_pred = results["violation_pred"].astype(int).values

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"\n--- Metrics ---")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1 Score:  {f1:.3f}")
    
    metrics = {"precision": precision, "recall": recall, "f1": f1}
    metrics_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mod3_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
        
    if f1 >= 0.75:
        print("[SUCCESS] F1 score >= 0.75")
    else:
        print("[FAIL] F1 score below threshold.")

if __name__ == "__main__":
    run_compliance_engine()
