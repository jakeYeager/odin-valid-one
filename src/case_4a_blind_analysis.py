"""
Case 4A: Energy-Weighted Clustering Patterns - Full Population (Blind Study - Approach Two)
Replicates Case 3A analysis but weights by energy proxy (10^(1.5 * v_val))
instead of event count. Tests whether clustering patterns are robust
to different analytical metrics.
Outputs results to output/case_4a_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4a_results_blind.json')
CASE_3A_RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3a_results_blind.json')

N_BINS = 16
N_SYNTHETIC = 1000
ALPHA = 0.05


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    print(f"  Loaded {len(df)} records from {path}")
    return df


def calculate_energy(v_vals):
    """Calculate energy proxy: energy = 10^(1.5 * v_val)."""
    return np.power(10, 1.5 * v_vals)


def bin_energy(values, energy, n_bins=N_BINS):
    """Bin values into n_bins equal-width bins from 0 to max(values).
    Returns energy sum per bin instead of count."""
    max_val = np.max(values)
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


def rayleigh_test(values, weights=None):
    """Energy-weighted Rayleigh test for circular concentration.
    Maps data to [0, 2*pi] and tests for directional clustering,
    weighting each event by its energy."""
    min_val = np.min(values)
    max_val = np.max(values)
    if max_val == min_val:
        return 0.0, 1.0
    theta = 2 * np.pi * (values - min_val) / (max_val - min_val)
    if weights is None:
        weights = np.ones_like(theta)
    n = len(theta)
    w_total = np.sum(weights)
    C = np.sum(weights * np.cos(theta)) / w_total
    S = np.sum(weights * np.sin(theta)) / w_total
    R_bar = np.sqrt(C**2 + S**2)
    Z = n * R_bar**2
    # Approximation (Greenwood & Durand, 1955)
    p_value = np.exp(-Z)
    p_value = p_value * (1 + (2 * Z - Z**2) / (4 * n)
                         - (24 * Z - 132 * Z**2 + 76 * Z**3 - 9 * Z**4) / (288 * n**2))
    p_value = max(0.0, min(1.0, float(p_value)))
    return float(Z), p_value


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


def analyze_variable_energy(values, energy, n_events):
    """Run energy-weighted clustering analysis on a single variable."""
    energy_per_bin, bin_edges, bin_size, bin_indices = bin_energy(values, energy)
    total_energy = np.sum(energy_per_bin)
    expected_energy = total_energy / N_BINS

    chi2_stat, chi2_p, dof = chi_square_energy(energy_per_bin)
    rayleigh_z, rayleigh_p = rayleigh_test(values, weights=energy)
    v = cramers_v(chi2_stat, n_events, N_BINS)

    residuals = standardized_residuals_energy(energy_per_bin, expected_energy)
    excess_bins, deficit_bins = identify_significant_bins(residuals)

    return {
        "chi_square_energy": {
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
        "energy_per_bin": [round(float(e), 4) for e in energy_per_bin],
        "expected_energy_per_bin": round(float(expected_energy), 4),
        "significant_bins_excess": excess_bins,
        "significant_bins_deficit": deficit_bins,
        "bin_edges": [round(float(e), 2) for e in bin_edges],
        "bin_size": round(float(bin_size), 2),
        "standardized_residuals": [round(float(r), 4) for r in residuals]
    }


def load_case_3a_results(path=CASE_3A_RESULTS_PATH):
    """Load Case 3A results for comparison."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  Warning: Case 3A results not found at {path}")
        return None


def run_synthetic_catalogs(df, energy, n_synthetic=N_SYNTHETIC):
    """Generate n_synthetic null hypothesis catalogs with energy weighting.
    Shuffles x_val, y_val, z_val randomly while keeping a_val and v_val
    (and thus energy) in original order."""
    variables = ['x_val', 'y_val', 'z_val']
    rng = np.random.default_rng(seed=42)

    synthetic_p_values = {var: [] for var in variables}
    synthetic_cramers_v = {var: [] for var in variables}

    n_records = len(df)

    for i in range(n_synthetic):
        for var in variables:
            # Shuffle the variable values randomly
            shuffled_values = rng.permutation(df[var].values)
            # Compute energy-weighted bins using original energy (v_val unchanged)
            energy_per_bin, _, _, _ = bin_energy(shuffled_values, energy)
            chi2_stat, chi2_p, _ = chi_square_energy(energy_per_bin)
            synthetic_p_values[var].append(chi2_p)
            v = cramers_v(chi2_stat, n_records, N_BINS)
            synthetic_cramers_v[var].append(v)

        if (i + 1) % 200 == 0:
            print(f"    Synthetic catalog {i + 1}/{n_synthetic} complete")

    return synthetic_p_values, synthetic_cramers_v


def percentile_rank(real_value, synthetic_values):
    """Calculate percentile rank of real_value in synthetic distribution."""
    arr = np.array(synthetic_values)
    return float(np.sum(arr <= real_value) / len(arr) * 100)


def main():
    print("Case 4A: Energy-Weighted Clustering Patterns - Full Population (Blind Study)")
    print("=" * 78)

    df = load_data()
    n = len(df)
    variables = ['x_val', 'y_val', 'z_val']

    # Verify all v_val > 0
    assert (df['v_val'] > 0).all(), "All v_val values must be > 0 for energy calculation"
    print(f"  All {n} v_val values > 0: verified")

    # Calculate energy
    energy = calculate_energy(df['v_val'].values)
    total_energy = float(np.sum(energy))
    print(f"  Total energy: {total_energy:.4e}")
    print(f"  Mean energy per event: {total_energy / n:.4e}")
    print(f"  Energy range: {np.min(energy):.4e} to {np.max(energy):.4e}")

    # Load Case 3A results for comparison
    case_3a = load_case_3a_results()

    # Analyze each variable
    print("\n  Analyzing variables (energy-weighted)...")
    var_results = {}
    for var in variables:
        result = analyze_variable_energy(df[var].values, energy, n)
        # Add Case 3A comparison
        if case_3a and var in case_3a:
            result["comparison_to_case_3a"] = {
                "case_3a_chi_square": case_3a[var]['chi_square']['statistic'],
                "case_3a_p_value": case_3a[var]['chi_square']['p_value'],
                "difference_note": "Energy-weighted result vs count-based result"
            }
        var_results[var] = result

        chi = result['chi_square_energy']
        ray = result['rayleigh']
        print(f"\n  {var}:")
        print(f"    Chi-square (energy): χ²={chi['statistic']}, p={chi['p_value']:.6e}, {chi['interpretation']}")
        print(f"    Rayleigh: Z={ray['statistic']}, p={ray['p_value']:.6e}")
        print(f"    Cramér's V: {result['cramers_v']}")
        print(f"    Significant bins - excess: {result['significant_bins_excess']}, "
              f"deficit: {result['significant_bins_deficit']}")

    # Generate synthetic null hypothesis catalogs
    print(f"\n  Generating {N_SYNTHETIC} synthetic null hypothesis catalogs (energy-weighted)...")
    synthetic_p_values, synthetic_cramers_v = run_synthetic_catalogs(df, energy, N_SYNTHETIC)

    # Percentile rank analysis
    print("\n  Percentile rank analysis:")
    percentile_results = {}
    for var in variables:
        real_p = var_results[var]['chi_square_energy']['p_value']
        pct = percentile_rank(real_p, synthetic_p_values[var])
        percentile_results[f"{var}_real_p_percentile"] = round(pct, 2)
        print(f"    {var}: real p-value at {pct:.1f}th percentile of synthetic distribution")

    # Assemble results
    results = {
        "sample_size": n,
        "total_energy": round(total_energy, 4),
        "energy_calculation": "energy = 10^(1.5 * v_val)",
        "binning_approach": "max(variable) / 16",
        "x_val": var_results['x_val'],
        "y_val": var_results['y_val'],
        "z_val": var_results['z_val'],
        "synthetic_null_hypothesis": {
            "synthetic_catalogs_generated": N_SYNTHETIC,
            "shuffling_method": "x_val, y_val, z_val randomized; a_val, v_val preserved",
            "energy_weighting_applied": True,
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
