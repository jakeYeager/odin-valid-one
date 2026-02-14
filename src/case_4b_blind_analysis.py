"""
Case 4B: Energy-Weighted Clustering Patterns - Stratified Population (Blind Study - Approach Two)
Replicates Case 3B stratified analysis but weights by energy proxy (10^(1.5 * v_val))
instead of event count. Tests whether energy-based clustering patterns persist
across v_val subpopulations.
Outputs results to output/case_4b_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4b_results_blind.json')
CASE_3B_RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3b_results_blind.json')
CASE_4A_RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4a_results_blind.json')

N_BINS = 16
N_SYNTHETIC = 100
ALPHA = 0.05


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    print(f"  Loaded {len(df)} records from {path}")
    return df


def calculate_energy(v_vals):
    """Calculate energy proxy: energy = 10^(1.5 * v_val)."""
    return np.power(10, 1.5 * v_vals)


def create_strata(df):
    """Stratify by v_val quartiles (4 groups), same as Case 3B."""
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


def bin_energy(values, energy, max_val, n_bins=N_BINS):
    """Bin values into n_bins equal-width bins using FULL DATASET max for consistency.
    Returns energy sum per bin instead of count."""
    bin_size = max_val / n_bins
    bin_edges = np.array([i * bin_size for i in range(n_bins + 1)])
    bin_indices = np.minimum(np.floor(values / bin_size).astype(int), n_bins - 1)

    energy_per_bin = np.zeros(n_bins)
    for i in range(n_bins):
        mask = bin_indices == i
        energy_per_bin[i] = np.sum(energy[mask])

    return energy_per_bin, bin_edges, bin_size, bin_indices


def chi_square_energy(observed_energy):
    """Chi-square goodness-of-fit test on energy distribution against uniform."""
    total = np.sum(observed_energy)
    expected = np.full(len(observed_energy), total / len(observed_energy))
    stat, p_value = stats.chisquare(observed_energy, f_exp=expected)
    dof = len(observed_energy) - 1
    return float(stat), float(p_value), dof


def cramers_v(chi2_stat, n, k):
    """Cramér's V = sqrt(chi2 / (n * (k - 1))).
    Based on COUNT (n = number of events), not energy, for comparability."""
    return float(np.sqrt(chi2_stat / (n * (k - 1))))


def standardized_residuals_energy(observed_energy, expected_energy):
    """Standardized residuals for energy: (observed - expected) / sqrt(expected)."""
    return (observed_energy - expected_energy) / np.sqrt(expected_energy)


def identify_significant_bins(residuals, threshold=2.0):
    """Bins with |residual| > threshold. Returns 1-indexed bin lists."""
    excess = [int(i + 1) for i in range(len(residuals)) if residuals[i] > threshold]
    deficit = [int(i + 1) for i in range(len(residuals)) if residuals[i] < -threshold]
    return excess, deficit


def analyze_variable_energy_in_stratum(values, energy, max_val, n_events):
    """Run energy-weighted clustering analysis on a single variable within a stratum."""
    energy_per_bin, bin_edges, bin_size, bin_indices = bin_energy(values, energy, max_val)
    total_energy = float(np.sum(energy_per_bin))
    expected_energy = total_energy / N_BINS

    chi2_stat, chi2_p, dof = chi_square_energy(energy_per_bin)
    v = cramers_v(chi2_stat, n_events, N_BINS)

    residuals = standardized_residuals_energy(energy_per_bin, expected_energy)
    excess_bins, deficit_bins = identify_significant_bins(residuals)

    verdict = "energy clustering" if chi2_p < ALPHA else "no energy clustering"

    return {
        "chi_square": round(chi2_stat, 4),
        "p_value": chi2_p,
        "degrees_of_freedom": dof,
        "cramers_v": round(v, 6),
        "verdict": verdict,
        "energy_per_bin": [round(float(e), 4) for e in energy_per_bin],
        "expected_energy_per_bin": round(float(expected_energy), 4),
        "total_energy": round(total_energy, 4),
        "bin_edges": [round(float(e), 2) for e in bin_edges],
        "bin_size": round(float(bin_size), 2),
        "standardized_residuals": [round(float(r), 4) for r in residuals],
        "significant_bins": {
            "excess": excess_bins,
            "deficit": deficit_bins
        }
    }


def load_comparison_results():
    """Load Case 3B and 4A results for comparison."""
    case_3b = None
    case_4a = None
    try:
        with open(CASE_3B_RESULTS_PATH, 'r') as f:
            case_3b = json.load(f)
    except FileNotFoundError:
        print(f"  Warning: Case 3B results not found at {CASE_3B_RESULTS_PATH}")
    try:
        with open(CASE_4A_RESULTS_PATH, 'r') as f:
            case_4a = json.load(f)
    except FileNotFoundError:
        print(f"  Warning: Case 4A results not found at {CASE_4A_RESULTS_PATH}")
    return case_3b, case_4a


def run_synthetic_catalogs_stratum(stratum_df, energy, max_vals, n_synthetic=N_SYNTHETIC):
    """Generate synthetic null catalogs for a single stratum (energy-weighted).
    Shuffles x_val, y_val, z_val within the stratum while keeping
    a_val and v_val (and thus energy) in original order."""
    variables = ['x_val', 'y_val', 'z_val']
    rng = np.random.default_rng(seed=42)
    n_records = len(stratum_df)

    synthetic_p_values = {var: [] for var in variables}

    for i in range(n_synthetic):
        for var in variables:
            shuffled_values = rng.permutation(stratum_df[var].values)
            energy_per_bin, _, _, _ = bin_energy(shuffled_values, energy, max_vals[var])
            _, chi2_p, _ = chi_square_energy(energy_per_bin)
            synthetic_p_values[var].append(chi2_p)

    return synthetic_p_values


def percentile_rank(real_value, synthetic_values):
    """Percentile rank of real_value in synthetic distribution."""
    arr = np.array(synthetic_values)
    return float(np.sum(arr <= real_value) / len(arr) * 100)


def main():
    print("Case 4B: Energy-Weighted Clustering Patterns - Stratified Population (Blind Study)")
    print("=" * 82)

    df = load_data()
    n_total = len(df)
    variables = ['x_val', 'y_val', 'z_val']

    # Verify all v_val > 0
    assert (df['v_val'] > 0).all(), "All v_val values must be > 0 for energy calculation"

    # Get full-dataset max values for consistent binning (same as Case 3B)
    max_vals = {var: float(np.max(df[var].values)) for var in variables}

    # Calculate energy for ALL records
    df['energy'] = calculate_energy(df['v_val'].values)
    total_energy_all = float(df['energy'].sum())

    # Create strata
    strata, quartiles = create_strata(df)

    print(f"\n  Total records: {n_total}")
    print(f"  Total energy: {total_energy_all:.4e}")
    print(f"  v_val quartiles: {[round(float(q), 4) for q in quartiles]}")
    print(f"  Full dataset max values: {max_vals}")

    stratum_sizes = {}
    stratum_energies = {}
    for label, sdf in strata.items():
        stratum_sizes[label] = len(sdf)
        stratum_energies[label] = round(float(sdf['energy'].sum()), 4)
        print(f"  {label}: {len(sdf)} records, energy={sdf['energy'].sum():.4e}")

    # Verify group sizes
    for label, size in stratum_sizes.items():
        assert size >= 100, f"Stratum {label} has only {size} records (< 100)"

    # Load comparison results
    case_3b, case_4a = load_comparison_results()

    results = {
        "stratification": "v_val quartiles (4 groups)",
        "total_sample_size": n_total,
        "energy_calculation": "energy = 10^(1.5 * v_val)",
        "v_val_quartiles": [round(float(q), 4) for q in quartiles],
        "full_dataset_max_values": {var: round(max_vals[var], 4) for var in variables},
        "stratum_sizes": stratum_sizes,
        "stratum_total_energies": stratum_energies,
    }

    stratum_labels = list(strata.keys())
    stratum_nums = ['stratum_1', 'stratum_2', 'stratum_3', 'stratum_4']

    for s_num, s_label in zip(stratum_nums, stratum_labels):
        sdf = strata[s_label]
        v_min = float(sdf['v_val'].min())
        v_max = float(sdf['v_val'].max())
        stratum_energy = sdf['energy'].values
        stratum_total_energy = float(np.sum(stratum_energy))
        n_stratum = len(sdf)

        print(f"\n  Analyzing {s_num} ({s_label}, n={n_stratum}, energy={stratum_total_energy:.4e})...")

        stratum_result = {
            "v_val_range": [round(v_min, 4), round(v_max, 4)],
            "sample_size": n_stratum,
            "total_energy": round(stratum_total_energy, 4),
            "mean_energy_per_event": round(stratum_total_energy / n_stratum, 4),
            "energy_range": [
                round(float(np.min(stratum_energy)), 4),
                round(float(np.max(stratum_energy)), 4)
            ],
        }

        # Analyze each variable (energy-weighted)
        for var in variables:
            var_result = analyze_variable_energy_in_stratum(
                sdf[var].values, stratum_energy, max_vals[var], n_stratum
            )

            # Comparison to Case 4A (full population)
            if case_4a and var in case_4a:
                case_4a_p = case_4a[var]['chi_square_energy']['p_value']
                case_4b_p = var_result['p_value']
                both_sig = (case_4a_p < ALPHA) and (case_4b_p < ALPHA)
                both_ns = (case_4a_p >= ALPHA) and (case_4b_p >= ALPHA)
                var_result['comparison_to_case_4a'] = "same pattern" if (both_sig or both_ns) else "different pattern"

            # Comparison to Case 3B (count-based stratified)
            s_idx = int(s_num.split('_')[1])
            if case_3b and f'stratum_{s_idx}' in case_3b:
                case_3b_stratum = case_3b[f'stratum_{s_idx}']
                if var in case_3b_stratum:
                    case_3b_p = case_3b_stratum[var]['p_value']
                    case_4b_p = var_result['p_value']
                    both_sig = (case_3b_p < ALPHA) and (case_4b_p < ALPHA)
                    both_ns = (case_3b_p >= ALPHA) and (case_4b_p >= ALPHA)
                    var_result['comparison_to_case_3b'] = "same pattern" if (both_sig or both_ns) else "different pattern"

            print(f"    {var}: chi2={var_result['chi_square']}, "
                  f"p={var_result['p_value']:.6e}, V={var_result['cramers_v']}, "
                  f"verdict={var_result['verdict']}")
            stratum_result[var] = var_result

        # Synthetic catalogs for this stratum (energy-weighted)
        print(f"    Generating {N_SYNTHETIC} synthetic catalogs (energy-weighted)...")
        synthetic_p = run_synthetic_catalogs_stratum(sdf, stratum_energy, max_vals)

        for var in variables:
            real_p = stratum_result[var]['p_value']
            pct = percentile_rank(real_p, synthetic_p[var])
            stratum_result[var]['synthetic_percentile'] = round(pct, 2)
            stratum_result[var]['synthetic_p_values'] = [round(p, 6) for p in synthetic_p[var]]
            print(f"    {var}: real p at {pct:.1f}th percentile of synthetic")

        results[s_num] = stratum_result

    # Comparative summary
    print("\n  Comparative Summary (Energy-Weighted):")
    comparative = {}
    for var in variables:
        verdicts = [results[s_num][var]['verdict'] for s_num in stratum_nums]
        all_clustering = all(v == "energy clustering" for v in verdicts)
        all_no_clustering = all(v == "no energy clustering" for v in verdicts)
        consistent = all_clustering or all_no_clustering
        comparative[f"{var}_consistent_across_strata"] = consistent
        comparative[f"{var}_verdicts"] = verdicts
        comparative[f"{var}_cramers_v_by_stratum"] = [
            results[s_num][var]['cramers_v'] for s_num in stratum_nums
        ]
        comparative[f"{var}_p_values_by_stratum"] = [
            results[s_num][var]['p_value'] for s_num in stratum_nums
        ]
        print(f"    {var}: consistent={consistent}, verdicts={verdicts}")

    # Determine if energy pattern is v_val-dependent
    any_consistent_clustering = any(
        comparative[f"{var}_consistent_across_strata"] and
        results['stratum_1'][var]['verdict'] == "energy clustering"
        for var in variables
    )
    comparative["energy_pattern_v_val_dependent"] = not any_consistent_clustering
    if any_consistent_clustering:
        comparative["interpretation"] = "energy clustering is universal (v_val-independent, persists across strata)"
    else:
        comparative["interpretation"] = "energy clustering is stratum-specific (v_val-dependent, varies across strata)"

    results["comparative_summary"] = comparative
    print(f"    Interpretation: {comparative['interpretation']}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
