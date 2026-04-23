import pandas as pd
import numpy as np
import os

# Paths
RAW_DATA_PATH = "data/raw_datasets/Road Constuction Delay Survey.csv"
OUTPUT_PATH = "data/execution_merged_real.csv"

def ingest_real_data():
    print(f"Loading raw survey data from {RAW_DATA_PATH}...")
    
    # Load with latin1 encoding due to special characters in headers
    try:
        df = pd.read_csv(RAW_DATA_PATH, encoding='latin1')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print(f"Original shape: {df.shape}")
    
    # The dataset is a survey where each row is a respondent's rating of different delay categories.
    # We will 'melt' this into a transactional log format (one row per project-task).
    
    # Identify category columns
    category_cols = [c for c in df.columns if 'Category' in c]
    respondent_info = [c for c in df.columns if 'Respondant' in c or 'Respondent' in c]
    
    # Melt the dataframe
    df_melted = df.melt(
        id_vars=respondent_info,
        value_vars=category_cols,
        var_name='raw_category',
        value_name='severity_score'
    )
    
    # Clean up names
    df_melted['delay_cause'] = df_melted['raw_category'].str.split(':').str[1].str.strip()
    df_melted['task_type'] = df_melted['delay_cause'].str.lower().str.replace(' ', '_')
    df_melted['project_id'] = "PROJ_REAL_" + df_melted['Respondent Number '].astype(str)
    
    # Convert severity_score to numeric, coercion will turn errors to NaN
    df_melted['severity_score'] = pd.to_numeric(df_melted['severity_score'], errors='coerce')
    
    # Filter out null severity scores
    df_melted = df_melted.dropna(subset=['severity_score'])
    
    # Map to our schema
    # Logic: 
    # 1. Planned Duration is a baseline (e.g., 60 days)
    # 2. Actual Duration = Planned + (Severity * 4) days of delay
    # 3. Violation = 1 if Severity >= 3
    
    BASELINE_PLANNED = 60
    df_melted['planned_duration_days'] = BASELINE_PLANNED
    df_melted['actual_duration_days'] = BASELINE_PLANNED + (df_melted['severity_score'] * 4)
    df_melted['violation'] = (df_melted['severity_score'] >= 3).astype(int)
    
    # Synthesize other features needed for our XGBoost pipeline
    # contractor_past_delay_rate (Randomized based on severity)
    df_melted['contractor_past_delay_rate'] = np.clip(
        (df_melted['severity_score'] / 5.0) + np.random.normal(0, 0.1, len(df_melted)), 
        0, 1
    )
    
    # is_monsoon_period (Randomly assign based on some categories)
    df_melted['is_monsoon_period'] = (df_melted['delay_cause'].str.contains('External', case=False)).astype(int)
    
    # Engineer the 5 missing columns from M4 schema
    df_melted['grace_period_days'] = np.random.randint(0, 8, len(df_melted))
    df_melted['material_supply_delay'] = (df_melted['task_type'] == 'materials').astype(int)
    df_melted['preceding_task_delayed'] = np.random.choice([0, 1], p=[0.7, 0.3], size=len(df_melted))
    df_melted['task_sequence_index'] = df_melted.groupby('project_id').cumcount()
    df_melted['penalty_per_day_inr'] = np.random.choice([5000, 10000, 15000, 20000, 25000], size=len(df_melted))
    
    # Add UI required columns
    df_melted['task_id'] = df_melted['project_id'] + '_' + df_melted['task_sequence_index'].astype(str)
    df_melted['delay_days'] = df_melted['actual_duration_days'] - df_melted['planned_duration_days']
    df_melted['penalty_amount_inr'] = df_melted['violation'] * df_melted['penalty_per_day_inr'] * df_melted['delay_days'].clip(lower=0)
    
    # Final Selection
    final_df = df_melted[[
        'project_id', 'task_id', 'task_type', 'planned_duration_days', 
        'actual_duration_days', 'violation', 'delay_cause', 
        'contractor_past_delay_rate', 'is_monsoon_period',
        'grace_period_days', 'material_supply_delay',
        'preceding_task_delayed', 'task_sequence_index',
        'penalty_per_day_inr', 'delay_days', 'penalty_amount_inr'
    ]]
    
    print("\n--- Real-World Dataset Verification ---")
    print(f"Final Shape: {final_df.shape}")
    print("\nViolation Class Distribution:")
    print(final_df['violation'].value_counts(normalize=True))
    
    print("\nSample Data:")
    print(final_df.head())
    
    # Save
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nReal-world merged execution log saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    ingest_real_data()
