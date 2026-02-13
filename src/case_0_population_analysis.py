"""
Case 0: Population Analysis - Blind Study (Approach Two)
Loads anonymized data and computes descriptive statistics for each column.
Outputs results to output/case_0_results.json.
"""

import json
import os
import pandas as pd
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_0_results.json')


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def compute_column_stats(df, col):
    return {
        "column_name": col,
        "total_count": int(df[col].count()),
        "min": float(df[col].min()),
        "max": float(df[col].max()),
        "mean": round(float(df[col].mean()), 4),
        "median": float(df[col].median()),
        "std_dev": round(float(df[col].std()), 4),
        "missing_count": int(df[col].isna().sum())
    }


def main():
    df = load_data()
    columns = ['a_val', 'v_val', 'x_val', 'y_val', 'z_val']

    column_stats = [compute_column_stats(df, col) for col in columns]

    unique_a_vals = sorted(df['a_val'].dropna().unique().tolist())
    a_val_counts = df['a_val'].value_counts().sort_index().to_dict()
    a_val_counts = {str(k): int(v) for k, v in a_val_counts.items()}

    results = {
        "case": "Case 0: Population Description",
        "approach": "Blind Study (Approach Two)",
        "total_records": len(df),
        "column_statistics": column_stats,
        "unique_a_values": unique_a_vals,
        "a_val_group_counts": a_val_counts
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results written to {OUTPUT_PATH}")
    print(f"Total records: {len(df)}")
    for stat in column_stats:
        print(f"  {stat['column_name']}: min={stat['min']}, max={stat['max']}, "
              f"mean={stat['mean']}, median={stat['median']}, std={stat['std_dev']}, "
              f"missing={stat['missing_count']}")
    print(f"Unique a_val values ({len(unique_a_vals)}): {unique_a_vals}")
    print(f"a_val group counts: {a_val_counts}")


if __name__ == '__main__':
    main()
