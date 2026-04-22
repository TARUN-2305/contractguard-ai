def agent_decide(violation_record, risk_score):
    """
    Rule-based agent. Takes a violation record + risk score.
    Returns a structured decision.
    """
    decisions = []
    
    # Rule 1: Confirmed violation -> trigger penalty
    if violation_record.get("violation") and violation_record.get("penalty_inr", 0) > 0:
        decisions.append({
            "action": "TRIGGER_PENALTY",
            "amount_inr": violation_record["penalty_inr"],
            "reason": f"Task overran deadline by {violation_record.get('overrun_days', 0)} days, "
                      f"exceeding grace period of {violation_record.get('grace_period_days', 0)} days."
        })
    
    # Rule 2: High risk upcoming task -> alert PM
    if risk_score >= 0.70:
        decisions.append({
            "action": "ALERT_PROJECT_MANAGER",
            "risk_score": round(risk_score, 2),
            "reason": "ML model predicts high probability of upcoming violation."
        })
    
    # Rule 3: Repeated contractor violations -> escalate
    if violation_record.get("contractor_past_delay_rate", 0) > 0.4 and \
       violation_record.get("violation"):
        decisions.append({
            "action": "ESCALATE_TO_AUDITOR",
            "reason": f"Contractor has historical delay rate of "
                      f"{violation_record['contractor_past_delay_rate']:.0%}."
        })
    
    # Rule 4: Low risk, compliant -> clear
    if not violation_record.get("violation") and risk_score < 0.30:
        decisions.append({
            "action": "CLEAR",
            "reason": "Task compliant. Low risk for next phase."
        })
    
    return decisions

if __name__ == "__main__":
    print("Testing Module 5: Agent Decision Layer...")
    
    # Test Rule 1 and Rule 3 bounds
    r13 = agent_decide({"violation": True, "overrun_days": 10, "grace_period_days": 2, "penalty_inr": 50000, "contractor_past_delay_rate": 0.5}, 0.5)
    r13_actions = [x['action'] for x in r13]
    assert "TRIGGER_PENALTY" in r13_actions, "Rule 1 Failed"
    assert "ESCALATE_TO_AUDITOR" in r13_actions, "Rule 3 Failed"
    
    # Test Rule 2 bounds
    r2 = agent_decide({"violation": False, "penalty_inr": 0}, 0.85)
    assert "ALERT_PROJECT_MANAGER" in [x['action'] for x in r2], "Rule 2 Failed"
    
    # Test Rule 4 bounds
    r4 = agent_decide({"violation": False, "penalty_inr": 0}, 0.15)
    assert "CLEAR" in [x['action'] for x in r4], "Rule 4 Failed"
    
    print("[SUCCESS] All 4 rule triggers fired perfectly against deterministic bounds.")
