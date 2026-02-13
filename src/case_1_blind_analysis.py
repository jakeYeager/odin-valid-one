"""
Case 1: Distribution Uniformity Testing - Blind Study (Approach Two)
Tests whether x_val, y_val, z_val show uniform or non-uniform distributions
across 16 equal-width bins using chi-square goodness-of-fit, Rayleigh test,
and Cramer's V effect size.
Outputs results to output/case_1_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_1_results_blind.json')

N_BINS = 16


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def bin_observations(series, n_bins=N_BINS):
    """Bin a series into n_bins equal-width bins across [min, max].
    Returns observed counts per bin and bin edges."""
    min_val = series.min()
    max_val = series.max()
    bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    # Use right=True so last bin includes max; first interval made inclusive via workaround
    bin_indices = np.digitize(series.values, bin_edges[1:-1], right=False)
    # bin_indices: 0 = [min, edge1), 1 = [edge1, edge2), ..., 15 = [edge15, max]
    counts = np.bincount(bin_indices, minlength=n_bins)[:n_bins]
    return counts, bin_edges


def chi_square_uniformity(counts):
    """Chi-square goodness-of-fit test against uniform distribution."""
    n = counts.sum()
    expected = np.full_like(counts, n / len(counts), dtype=float)
    stat, p_value = stats.chisquare(counts, f_exp=expected)
    return float(stat), float(p_value), len(counts) - 1


def rayleigh_test(series):
    """Rayleigh test for directional uniformity.
    Maps data range to [0, 2*pi] and tests for concentration.
    Z = n * R_bar^2, where R_bar is the mean resultant length.
    p-value approximated as exp(-Z) for large n."""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return 0.0, 1.0
    theta = 2 * np.pi * (series.values - min_val) / (max_val - min_val)
    n = len(theta)
    C = np.sum(np.cos(theta))
    S = np.sum(np.sin(theta))
    R_bar = np.sqrt(C**2 + S**2) / n
    Z = n * R_bar**2
    # Approximation valid for large n
    p_value = np.exp(-Z)
    # Correction for small samples (Greenwood & Durand, 1955)
    p_value = p_value * (1 + (2 * Z - Z**2) / (4 * n) - (24 * Z - 132 * Z**2 + 76 * Z**3 - 9 * Z**4) / (288 * n**2))
    p_value = max(0.0, min(1.0, p_value))
    return float(Z), float(p_value)


def cramers_v(chi2_stat, n, k):
    """Cramer's V effect size: sqrt(chi2 / (n * (k - 1)))."""
    return float(np.sqrt(chi2_stat / (n * (k - 1))))


def analyze_variable(series):
    """Run full uniformity analysis on a single variable."""
    counts, bin_edges = bin_observations(series)
    n = int(series.count())
    k = N_BINS

    chi2_stat, chi2_p, dof = chi_square_uniformity(counts)
    rayleigh_z, rayleigh_p = rayleigh_test(series)
    v = cramers_v(chi2_stat, n, k)

    return {
        "chi_square": {
            "statistic": round(chi2_stat, 4),
            "p_value": chi2_p,
            "degrees_of_freedom": dof,
            "interpretation": "significant" if chi2_p < 0.05 else "not significant"
        },
        "rayleigh": {
            "statistic": round(rayleigh_z, 4),
            "p_value": rayleigh_p
        },
        "effect_size_cramers_v": round(v, 6),
        "sample_size": n,
        "bin_counts": counts.tolist(),
        "expected_count_per_bin": round(n / k, 2),
        "bin_edges": [round(float(e), 2) for e in bin_edges]
    }


def main():
    df = load_data()
    variables = ['x_val', 'y_val', 'z_val']

    results = {}
    for var in variables:
        results[var] = analyze_variable(df[var])

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results written to {OUTPUT_PATH}")
    for var in variables:
        r = results[var]
        chi = r['chi_square']
        ray = r['rayleigh']
        print(f"\n  {var}:")
        print(f"    Chi-square: X2={chi['statistic']}, p={chi['p_value']:.6e}, "
              f"df={chi['degrees_of_freedom']}, {chi['interpretation']}")
        print(f"    Rayleigh: Z={ray['statistic']}, p={ray['p_value']:.6e}")
        print(f"    Cramer's V: {r['effect_size_cramers_v']}")
        print(f"    Bin counts: {r['bin_counts']}")


if __name__ == '__main__':
    main()
