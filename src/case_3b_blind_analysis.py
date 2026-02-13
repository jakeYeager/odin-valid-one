"""
Case 3B: Clustering Patterns - Stratified Population (Blind Study - Approach Two)
Tests whether clustering patterns from Case 3A persist when data is stratified
by v_val quartiles. Uses chi-square goodness-of-fit, Cramér's V effect size,
and 100 synthetic null hypothesis catalogs per stratum.
Outputs results to output/case_3b_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3b_results_blind.json')

N_BINS = 16
N_SYNTHETIC = 100
ALPHA = 0.05


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    print(f"  Loaded {len(df)} records from {path}")
    return df


def create_strata(df):
    """Stratify by v_val quartiles (4 groups)."""
    quartiles = df['v_val'].quantile([0.25, 0.50, 0.75]).values
    conditions = [
        df['v_val'] <= quartiles[0],
        (df['v_val'] > quartiles[0]) & (df['v_val'] <= quartiles[1]),
        (df['v_val'] > quartiles[1]) & (df['v_val'] <= quartiles[2]),
        df['v_val'] > quartiles[2],
    ]
    labels = ['group_1_0_25pct', 'group_2_25_50pct', 'group_3_50_75pct', 'group_4_75_100pct']
    strata = {}
    for label, cond in zip(labels, conditions):
        strata[label] = df[cond].copy()
    return strata, quartiles


def bin_observations(values, max_val, n_bins=N_BINS):
    """Bin values into n_bins equal-width bins using FULL DATASET max for consistency."""
    bin_size = max_val / n_bins
    bin_edges = np.array([i * bin_size for i in range(n_bins + 1)])
    bin_indices = np.minimum(np.floor(values / bin_size).astype(int), n_bins - 1)
    counts = np.bincount(bin_indices, minlength=n_bins)[:n_bins]
    return counts, bin_edges, bin_size


def chi_square_uniformity(counts):
    """Chi-square goodness-of-fit test against uniform distribution."""
    n = int(counts.sum())
    expected = np.full(len(counts), n / len(counts), dtype=float)
    stat, p_value = stats.chisquare(counts, f_exp=expected)
    dof = len(counts) - 1
    return float(stat), float(p_value), dof


def cramers_v(chi2_stat, n, k):
    """Cramér's V = sqrt(chi2 / (n * (k - 1)))."""
    return float(np.sqrt(chi2_stat / (n * (k - 1))))


def standardized_residuals(counts, expected):
    """(observed - expected) / sqrt(expected)."""
    return (counts - expected) / np.sqrt(expected)


def identify_significant_bins(residuals, threshold=2.0):
    """Bins with |residual| > threshold. Returns 1-indexed lists."""
    excess = [int(i + 1) for i in range(len(residuals)) if residuals[i] > threshold]
    deficit = [int(i + 1) for i in range(len(residuals)) if residuals[i] < -threshold]
    return excess, deficit


def analyze_variable_in_stratum(values, max_val):
    """Run clustering analysis on a single variable within a stratum."""
    n = len(values)
    counts, bin_edges, bin_size = bin_observations(values, max_val)
    expected = n / N_BINS

    chi2_stat, chi2_p, dof = chi_square_uniformity(counts)
    v = cramers_v(chi2_stat, n, N_BINS)

    residuals = standardized_residuals(counts.astype(float), expected)
    excess_bins, deficit_bins = identify_significant_bins(residuals)

    verdict = "clustering" if chi2_p < ALPHA else "no clustering"

    return {
        "chi_square": round(chi2_stat, 4),
        "p_value": chi2_p,
        "degrees_of_freedom": dof,
        "cramers_v": round(v, 6),
        "verdict": verdict,
        "bin_counts": counts.tolist(),
        "expected_count_per_bin": round(expected, 2),
        "bin_edges": [round(float(e), 2) for e in bin_edges],
        "bin_size": round(float(bin_size), 2),
        "standardized_residuals": [round(float(r), 4) for r in residuals],
        "significant_bins": {
            "excess": excess_bins,
            "deficit": deficit_bins
        }
    }


def run_synthetic_catalogs_stratum(stratum_df, max_vals, n_synthetic=N_SYNTHETIC):
    """Generate synthetic null catalogs for a single stratum.
    Generates uniform random values in [0, max(variable)] for each variable."""
    variables = ['x_val', 'y_val', 'z_val']
    rng = np.random.default_rng(seed=42)
    n_records = len(stratum_df)

    synthetic_p_values = {var: [] for var in variables}

    for i in range(n_synthetic):
        for var in variables:
            synthetic_values = rng.uniform(0, max_vals[var], size=n_records)
            counts, _, _ = bin_observations(synthetic_values, max_vals[var])
            _, chi2_p, _ = chi_square_uniformity(counts)
            synthetic_p_values[var].append(chi2_p)

    return synthetic_p_values


def percentile_rank(real_value, synthetic_values):
    """Percentile rank of real_value in synthetic distribution."""
    arr = np.array(synthetic_values)
    return float(np.sum(arr <= real_value) / len(arr) * 100)


def main():
    print("Case 3B: Clustering Patterns - Stratified Population (Blind Study)")
    print("=" * 72)

    df = load_data()
    n_total = len(df)
    variables = ['x_val', 'y_val', 'z_val']

    # Get full-dataset max values for consistent binning
    max_vals = {var: float(np.max(df[var].values)) for var in variables}

    # Create strata
    strata, quartiles = create_strata(df)

    print(f"\n  Total records: {n_total}")
    print(f"  v_val quartiles: {[round(float(q), 4) for q in quartiles]}")
    stratum_sizes = {}
    for label, sdf in strata.items():
        stratum_sizes[label] = len(sdf)
        print(f"  {label}: {len(sdf)} records")

    # Verify group sizes
    for label, size in stratum_sizes.items():
        assert size >= 100, f"Stratum {label} has only {size} records (< 100)"

    results = {
        "stratification": "v_val quartiles (4 groups)",
        "total_sample_size": n_total,
        "v_val_quartiles": [round(float(q), 4) for q in quartiles],
        "full_dataset_max_values": {var: round(max_vals[var], 4) for var in variables},
        "stratum_sizes": stratum_sizes,
    }

    stratum_labels = list(strata.keys())
    stratum_nums = ['stratum_1', 'stratum_2', 'stratum_3', 'stratum_4']

    for s_num, s_label in zip(stratum_nums, stratum_labels):
        sdf = strata[s_label]
        v_min = float(sdf['v_val'].min())
        v_max = float(sdf['v_val'].max())

        print(f"\n  Analyzing {s_num} ({s_label}, n={len(sdf)})...")

        stratum_result = {
            "v_val_range": [round(v_min, 4), round(v_max, 4)],
            "sample_size": len(sdf),
        }

        # Analyze each variable
        for var in variables:
            var_result = analyze_variable_in_stratum(sdf[var].values, max_vals[var])
            print(f"    {var}: χ²={var_result['chi_square']}, "
                  f"p={var_result['p_value']:.6e}, V={var_result['cramers_v']}, "
                  f"verdict={var_result['verdict']}")
            stratum_result[var] = var_result

        # Synthetic catalogs for this stratum
        print(f"    Generating {N_SYNTHETIC} synthetic catalogs...")
        synthetic_p = run_synthetic_catalogs_stratum(sdf, max_vals)

        for var in variables:
            real_p = stratum_result[var]['p_value']
            pct = percentile_rank(real_p, synthetic_p[var])
            stratum_result[var]['synthetic_percentile'] = round(pct, 2)
            stratum_result[var]['synthetic_p_values'] = [round(p, 6) for p in synthetic_p[var]]
            print(f"    {var}: real p at {pct:.1f}th percentile of synthetic")

        results[s_num] = stratum_result

    # Comparative summary
    print("\n  Comparative Summary:")
    comparative = {}
    for var in variables:
        verdicts = [results[s_num][var]['verdict'] for s_num in stratum_nums]
        all_clustering = all(v == "clustering" for v in verdicts)
        all_no_clustering = all(v == "no clustering" for v in verdicts)
        consistent = all_clustering or all_no_clustering
        comparative[f"{var}_consistent"] = consistent
        comparative[f"{var}_verdicts"] = verdicts
        comparative[f"{var}_cramers_v_by_stratum"] = [
            results[s_num][var]['cramers_v'] for s_num in stratum_nums
        ]
        print(f"    {var}: consistent={consistent}, verdicts={verdicts}")

    # Determine overall interpretation
    any_consistent_clustering = any(
        comparative[f"{var}_consistent"] and
        results['stratum_1'][var]['verdict'] == "clustering"
        for var in variables
    )
    if any_consistent_clustering:
        comparative["interpretation"] = "clustering pattern is v_val-independent (persists across strata)"
    else:
        comparative["interpretation"] = "clustering pattern is v_val-dependent (varies across strata)"

    results["comparative_summary"] = comparative
    print(f"    Interpretation: {comparative['interpretation']}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
