import os
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import wandb
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import classification_report, roc_auc_score, recall_score
from imblearn.over_sampling import ADASYN
import json

def run_risk_predictor():
    print("Starting Module 4: Risk Predictor")
    
    # Init Tracking (offline mode to bypass API key)
    os.environ["WANDB_MODE"] = "offline"
    wandb.init(project="contractguard-risk", name="xgb-v1")

    # Load data
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'execution_merged.csv')
    df = pd.read_csv(csv_path)

    FEATURES = [
        "planned_duration_days",
        "grace_period_days",
        "contractor_past_delay_rate",
        "is_monsoon_period",
        "material_supply_delay",
        "preceding_task_delayed",
        "task_sequence_index",
        "penalty_per_day_inr"
    ]

    X = df[FEATURES].fillna(0)
    y = df["violation"]
    
    print(f"Violation rate (Minority Class): {y.mean():.2%}")
    
    # Handle Imbalance
    adasyn = ADASYN(random_state=42)
    X_res, y_res = adasyn.fit_resample(X, y)

    # Train
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        scale_pos_weight=1.5,
        random_state=42
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_res, y_res, cv=cv, scoring="roc_auc")
    print(f"CV AUROC: {scores.mean():.3f} ± {scores.std():.3f}")

    # Evaluate
    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, stratify=y_res, random_state=42)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    auroc = roc_auc_score(y_test, y_prob)
    print(classification_report(y_test, y_pred))
    print(f"Test AUROC: {auroc:.3f}")
    
    # Calculate minority recall
    minority_recall = recall_score(y_test, y_pred, pos_label=1)
    print(f"Minority Recall: {minority_recall:.3f}")

    # Log to wandb
    wandb.log({
        "auroc": auroc,
        "minority_recall": minority_recall,
        "cv_auroc_mean": scores.mean(),
        "cv_auroc_std": scores.std()
    })

    # Explain with SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    import matplotlib.pyplot as plt
    shap.summary_plot(shap_values, X_test, show=False)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'models'), exist_ok=True)
    shap_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'shap_summary.png')
    plt.savefig(shap_path, bbox_inches="tight")
    wandb.log({"shap_summary": wandb.Image(shap_path)})
    
    # Save Model
    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'models', 'risk_predictor_v1.json')
    model.save_model(model_path)
    print(f"Model saved to {model_path}.")
    
    metrics = {"auroc": auroc, "minority_recall": minority_recall}
    metrics_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mod4_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f)
        
    if auroc >= 0.78 and minority_recall >= 0.70:
        print("[SUCCESS] Go/No-Go Criteria Met!")
    else:
        print("[FAIL] Criteria not met.")
        exit(1)

if __name__ == "__main__":
    run_risk_predictor()
