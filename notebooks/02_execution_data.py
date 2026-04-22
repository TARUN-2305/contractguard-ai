import pandas as pd
import numpy as np
import random
import os
import json
from faker import Faker

def generate_execution_data():
    print("Starting Module 2...")
    fake = Faker()
    random.seed(42)
    np.random.seed(42)

    # Load extracted rules dynamically
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rule_store', 'contract_001_rules.json')
    with open(rules_path, 'r') as f:
        rules = json.load(f)
        
    # Get exact tasks from the LLM extraction
    ROAD_TASKS = [r['task_name'] for r in rules]
    
    if not ROAD_TASKS:
        raise ValueError("No tasks found in rule_store!")

    DELAY_CAUSES = [
        "material_shortage", "rain_monsoon", "equipment_breakdown",
        "labour_dispute", "land_acquisition", "utility_shifting",
        "design_change", "subcontractor_failure", "on_schedule"
    ]

    def generate_project(project_id, n_tasks):
        rows = []
        contractor_delay_rate = round(random.uniform(0.1, 0.6), 2)  
        
        # sample task subset per project
        project_tasks = random.sample(ROAD_TASKS, k=min(n_tasks, len(ROAD_TASKS)))
        
        for i, task_name in enumerate(project_tasks):
            # Find rule to get the baseline synthetic boundaries
            rule = next(r for r in rules if r['task_name'] == task_name)
            planned_days = rule.get('deadline_days') or random.randint(15, 90)
            grace_days = rule.get('grace_period_days') or 0
            penalty_per_day = rule.get('penalty_per_day_inr') or 10000 

            delay_prob = (
                0.15 +
                0.20 * contractor_delay_rate +
                0.15 * (1 if 'monsoon' in task_name else 0) +
                0.10 * (i / n_tasks) 
            )
            
            is_delayed = random.random() < delay_prob
            
            if is_delayed:
                delay_days = random.randint(1, int(planned_days * 0.6) + 5)
                actual_days = planned_days + delay_days
                cause = random.choice(DELAY_CAUSES[:-1])
            else:
                actual_days = random.randint(int(planned_days * 0.8), planned_days)
                delay_days = 0
                cause = "on_schedule"
            
            # Ground truth calculation logic based exactly on contract compliance 
            # Note: We simulate ground truth strictly according to rule to ensure ML can learn it
            overrun = actual_days - planned_days
            violation = overrun > grace_days
            penalty_amount = max(0, (overrun - grace_days)) * penalty_per_day if violation else 0
            
            rows.append({
                "project_id": project_id,
                "task_id": f"{project_id}_T{i+1:02d}",
                "task_type": task_name,
                "planned_duration_days": planned_days,
                "actual_duration_days": actual_days,
                "delay_days": delay_days,
                "grace_period_days": grace_days,
                "penalty_per_day_inr": penalty_per_day,
                "contractor_past_delay_rate": contractor_delay_rate,
                "is_monsoon_period": random.choice([0, 1]),
                "material_supply_delay": 1 if cause == "material_shortage" else 0,
                "preceding_task_delayed": 1 if i > 0 and rows[-1]["delay_days"] > 0 else 0,
                "task_sequence_index": i,
                "delay_cause": cause,
                "violation": int(violation),
                "penalty_amount_inr": penalty_amount,
                "data_source": "synthetic"
            })
        return rows

    # Generate 1000 projects to ensure enough data for XGBoost in Mod 4
    all_rows = []
    for pid in range(1, 1001):
        num_tasks_for_proj = random.randint(3, len(ROAD_TASKS))
        all_rows.extend(generate_project(f"PROJ_{pid:04d}", num_tasks_for_proj))

    df = pd.DataFrame(all_rows)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'execution_merged.csv')
    df.to_csv(out_path, index=False)
    
    print(f"[SUCCESS] Generated {len(df)} task records across {df.project_id.nunique()} projects")
    print(f"Violation rate: {df.violation.mean():.2%}")
    print(f"Data saved to: {out_path}")

if __name__ == "__main__":
    generate_execution_data()
