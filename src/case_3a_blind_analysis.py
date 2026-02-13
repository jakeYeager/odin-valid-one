"""
Case 3A: Clustering Patterns - Full Population (Blind Study - Approach Two)
Tests whether x_val, y_val, z_val show clustering patterns across 16 equal bins
using chi-square goodness-of-fit, Rayleigh test, Cramér's V effect size,
standardized residuals, and 1000 synthetic null hypothesis catalogs.
Outputs results to output/case_3a_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3a_results_blind.json')

N_BINS = 16
N_SYNTHETIC = 1000
ALPHA = 0.05


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    print(f"  Loaded {len(df)} records from {path}")
    return df


def bin_observations(values, n_bins=N_BINS):
    """Bin values into n_bins equal-width bins from 0 to max(values).
    Bin size = max(values) / n_bins as specified."""
    max_val = np.max(values)
    bin_size = max_val / n_bins
    bin_edges = np.array([i * bin_size for i in range(n_bins + 1)])
    # Assign bins: values in [0, bin_size) -> bin 0, etc.
    # Last bin includes max value
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


def rayleigh_test(values):
    """Rayleigh test for circular concentration.
    Maps data to [0, 2*pi] and tests for directional clustering."""
    min_val = np.min(values)
    max_val = np.max(values)
    if max_val == min_val:
        return 0.0, 1.0
    theta = 2 * np.pi * (values - min_val) / (max_val - min_val)
    n = len(theta)
    C = np.sum(np.cos(theta))
    S = np.sum(np.sin(theta))
    R_bar = np.sqrt(C**2 + S**2) / n
    Z = n * R_bar**2
    # Approximation with correction (Greenwood & Durand, 1955)
    p_value = np.exp(-Z)
    p_value = p_value * (1 + (2 * Z - Z**2) / (4 * n)
                         - (24 * Z - 132 * Z**2 + 76 * Z**3 - 9 * Z**4) / (288 * n**2))
    p_value = max(0.0, min(1.0, float(p_value)))
    return float(Z), p_value


def cramers_v(chi2_stat, n, k):
    """Cramér's V = sqrt(chi2 / (n * (k - 1)))."""
    return float(np.sqrt(chi2_stat / (n * (k - 1))))


def standardized_residuals(counts, expected):
    """Calculate standardized residuals: (observed - expected) / sqrt(expected)."""
    return (counts - expected) / np.sqrt(expected)


def identify_significant_bins(residuals, threshold=2.0):
    """Bins with |residual| > threshold are significant.
    Returns excess (positive) and deficit (negative) bin indices (1-indexed)."""
    excess = [int(i + 1) for i in range(len(residuals)) if residuals[i] > threshold]
    deficit = [int(i + 1) for i in range(len(residuals)) if residuals[i] < -threshold]
    return excess, deficit


def analyze_variable(values):
    """Run full clustering analysis on a single variable."""
    n = len(values)
    counts, bin_edges, bin_size = bin_observations(values)
    expected = n / N_BINS

    chi2_stat, chi2_p, dof = chi_square_uniformity(counts)
    rayleigh_z, rayleigh_p = rayleigh_test(values)
    v = cramers_v(chi2_stat, n, N_BINS)

    residuals = standardized_residuals(counts.astype(float), expected)
    excess_bins, deficit_bins = identify_significant_bins(residuals)

    return {
        "chi_square": {
            "statistic": round(chi2_stat, 4),
            "p_value": chi2_p,
            "degrees_of_freedom": dof,
            "interpretation": "significant" if chi2_p < ALPHA else "not significant"
        },
        "rayleigh": {
            "statistic": round(rayleigh_z, 4),
            "p_value": rayleigh_p
        },
        "cramers_v": round(v, 6),
        "significant_bins": {
            "excess": excess_bins,
            "deficit": deficit_bins
        },
        "bin_counts": counts.tolist(),
        "expected_count_per_bin": round(expected, 2),
        "bin_edges": [round(float(e), 2) for e in bin_edges],
        "bin_size": round(float(bin_size), 2),
        "standardized_residuals": [round(float(r), 4) for r in residuals]
    }


def run_synthetic_catalogs(df, n_synthetic=N_SYNTHETIC):
    """Generate n_synthetic null hypothesis catalogs.
    For each variable, generates N uniform random values in [0, max(variable)]
    and runs identical chi-square analysis. This tests whether the observed
    distribution differs from true uniformity (the null hypothesis).
    Note: Simple permutation of existing values preserves the marginal distribution
    and would yield identical bin counts, so uniform random generation is used instead."""
    variables = ['x_val', 'y_val', 'z_val']
    rng = np.random.default_rng(seed=42)

    synthetic_p_values = {var: [] for var in variables}
    synthetic_cramers_v = {var: [] for var in variables}

    # Cache max values for each variable
    max_vals = {var: np.max(df[var].values) for var in variables}
    n_records = len(df)

    for i in range(n_synthetic):
        for var in variables:
            # Generate uniform random values in [0, max(variable)]
            synthetic_values = rng.uniform(0, max_vals[var], size=n_records)
            counts, _, _ = bin_observations(synthetic_values)
            chi2_stat, chi2_p, _ = chi_square_uniformity(counts)
            synthetic_p_values[var].append(chi2_p)
            n = n_records
            v = cramers_v(chi2_stat, n, N_BINS)
            synthetic_cramers_v[var].append(v)

        if (i + 1) % 200 == 0:
            print(f"    Synthetic catalog {i + 1}/{n_synthetic} complete")

    return synthetic_p_values, synthetic_cramers_v


def percentile_rank(real_value, synthetic_values):
    """Calculate percentile rank of real_value in synthetic distribution."""
    arr = np.array(synthetic_values)
    return float(np.sum(arr <= real_value) / len(arr) * 100)


def main():
    print("Case 3A: Clustering Patterns - Full Population (Blind Study)")
    print("=" * 72)

    df = load_data()
    n = len(df)
    variables = ['x_val', 'y_val', 'z_val']

    # Analyze each variable
    print("\n  Analyzing variables...")
    var_results = {}
    for var in variables:
        var_results[var] = analyze_variable(df[var].values)
        chi = var_results[var]['chi_square']
        ray = var_results[var]['rayleigh']
        print(f"\n  {var}:")
        print(f"    Chi-square: χ²={chi['statistic']}, p={chi['p_value']:.6e}, {chi['interpretation']}")
        print(f"    Rayleigh: Z={ray['statistic']}, p={ray['p_value']:.6e}")
        print(f"    Cramér's V: {var_results[var]['cramers_v']}")
        print(f"    Significant bins - excess: {var_results[var]['significant_bins']['excess']}, "
              f"deficit: {var_results[var]['significant_bins']['deficit']}")

    # Generate synthetic null hypothesis catalogs
    print(f"\n  Generating {N_SYNTHETIC} synthetic null hypothesis catalogs...")
    synthetic_p_values, synthetic_cramers_v = run_synthetic_catalogs(df, N_SYNTHETIC)

    # Percentile rank analysis
    print("\n  Percentile rank analysis:")
    percentile_results = {}
    for var in variables:
        real_p = var_results[var]['chi_square']['p_value']
        pct = percentile_rank(real_p, synthetic_p_values[var])
        percentile_results[f"{var}_real_p_percentile"] = round(pct, 2)
        print(f"    {var}: real p-value at {pct:.1f}th percentile of synthetic distribution")

    # Assemble results
    results = {
        "sample_size": n,
        "binning_approach": "max(variable) / 16",
        "x_val": var_results['x_val'],
        "y_val": var_results['y_val'],
        "z_val": var_results['z_val'],
        "synthetic_null_hypothesis": {
            "synthetic_catalogs_generated": N_SYNTHETIC,
            "shuffling_method": "Uniform random values in [0, max(variable)] for x_val, y_val, z_val; tests observed distribution against true uniform null",
            "x_val_synthetic_p_values": [round(p, 6) for p in synthetic_p_values['x_val']],
            "y_val_synthetic_p_values": [round(p, 6) for p in synthetic_p_values['y_val']],
            "z_val_synthetic_p_values": [round(p, 6) for p in synthetic_p_values['z_val']],
            "x_val_synthetic_cramers_v": [round(v, 6) for v in synthetic_cramers_v['x_val']],
            "y_val_synthetic_cramers_v": [round(v, 6) for v in synthetic_cramers_v['y_val']],
            "z_val_synthetic_cramers_v": [round(v, 6) for v in synthetic_cramers_v['z_val']],
            "percentile_rank_analysis": percentile_results
        }
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
