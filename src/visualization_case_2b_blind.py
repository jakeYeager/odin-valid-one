"""
Case 2B: Visualization - Blind Study (Approach Two)
Generates 4 plots for inter-event interval analysis on filtered population (v_val 6.0-6.9):
  1. Linear histogram of raw intervals
  2. Log-space histogram with uniform baseline
  3. Q-Q plot against exponential distribution
  4. Sorted interval plot (log scale)
All outputs saved to output/ directory.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'timestamp_vals.csv')
RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_2b_results_blind.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

N_BINS = 16
V_VAL_MIN = 6.0
V_VAL_MAX = 6.9


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def load_intervals(path=DATA_PATH):
    """Load, filter to v_val 6.0-6.9, and compute intervals from raw timestamp data."""
    import pandas as pd
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df[(df['v_val'] >= V_VAL_MIN) & (df['v_val'] <= V_VAL_MAX)].copy()
    df = df.sort_values('timestamp').reset_index(drop=True)
    deltas = df['timestamp'].diff().dropna()
    interval_days = deltas.dt.total_seconds() / 86400.0
    return interval_days[interval_days > 0].values


def make_histogram_linear(intervals, results, output_dir):
    """Histogram of raw intervals with mean and median lines."""
    ist = results['interval_statistics']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(intervals, bins=50, color='#2980b9', edgecolor='black', linewidth=0.5, alpha=0.8)
    ax.axvline(ist['mean_days'], color='#c0392c', linestyle='--', linewidth=1.5,
               label=f"Mean: {ist['mean_days']:.2f} days")
    ax.axvline(ist['median_days'], color='#27ae60', linestyle='-', linewidth=1.5,
               label=f"Median: {ist['median_days']:.2f} days")
    ax.set_xlabel('Interval (days)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Inter-Event Intervals (Linear, v_val 6.0-6.9)')
    ax.legend()
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_2b_histogram_linear_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_histogram_log(intervals, results, output_dir):
    """Histogram of log10-transformed intervals with uniform baseline."""
    log_intervals = np.log10(intervals)
    bin_counts = results['uniformity_test']['bin_counts']
    p_value = results['uniformity_test']['chi_square']['p_value']
    chi2 = results['uniformity_test']['chi_square']['statistic']

    min_log = log_intervals.min()
    max_log = log_intervals.max()
    bin_edges = np.linspace(min_log, max_log, N_BINS + 1)

    expected = sum(bin_counts) / N_BINS

    fig, ax = plt.subplots(figsize=(10, 6))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    colors = ['#c0392c' if c > expected else '#2980b9' for c in bin_counts]
    ax.bar(bin_centers, bin_counts, width=(max_log - min_log) / N_BINS * 0.9,
           color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(y=expected, color='black', linestyle='--', linewidth=1.5,
               label=f'Expected (uniform): {expected:.1f}')
    ax.set_xlabel('log\u2081\u2080(Interval in days)')
    ax.set_ylabel('Count')
    sig_label = "SIGNIFICANT" if p_value < 0.05 else "not significant"
    ax.set_title(f'Distribution of Inter-Event Intervals (Log-space, v_val 6.0-6.9)\n'
                 f'\u03c7\u00b2 = {chi2:.2f}, p = {p_value:.4e} ({sig_label})')
    ax.legend()
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_2b_histogram_log_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_qq_plot(intervals, results, output_dir):
    """Q-Q plot comparing observed intervals to exponential distribution."""
    mean_interval = np.mean(intervals)
    sorted_intervals = np.sort(intervals)
    n = len(sorted_intervals)
    theoretical_quantiles = stats.expon.ppf(np.arange(1, n + 1) / (n + 1), scale=mean_interval)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(theoretical_quantiles, sorted_intervals, s=2, alpha=0.4, color='#2980b9')

    # Reference line
    max_val = max(theoretical_quantiles.max(), sorted_intervals.max())
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=1.5, label='y = x (perfect exponential fit)')

    ks_p = results['exponential_baseline_test']['ks_p_value']
    ks_d = results['exponential_baseline_test']['ks_statistic']
    ax.set_xlabel('Theoretical Quantiles (Exponential)')
    ax.set_ylabel('Observed Quantiles (Interval Days)')
    ax.set_title(f'Q-Q Plot: Observed vs Exponential (v_val 6.0-6.9)\n'
                 f'KS D = {ks_d:.4f}, p = {ks_p:.4e}')
    ax.legend()
    ax.set_aspect('equal', adjustable='datalim')
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_2b_qq_plot_exponential_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_sorted_intervals(intervals, results, output_dir):
    """Sorted interval plot showing rank vs duration on log scale."""
    sorted_vals = np.sort(intervals)
    ranks = np.arange(1, len(sorted_vals) + 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ranks, sorted_vals, color='#2980b9', linewidth=0.8)
    ax.set_yscale('log')
    ax.set_xlabel('Interval Rank (shortest \u2192 longest)')
    ax.set_ylabel('Interval Duration (days, log scale)')
    ax.set_title('Sorted Intervals (v_val 6.0-6.9)')

    # Mark mean and median
    mean_val = results['interval_statistics']['mean_days']
    median_val = results['interval_statistics']['median_days']
    ax.axhline(y=mean_val, color='#c0392c', linestyle='--', linewidth=1,
               label=f'Mean: {mean_val:.2f} days')
    ax.axhline(y=median_val, color='#27ae60', linestyle='-', linewidth=1,
               label=f'Median: {median_val:.2f} days')
    ax.legend()
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_2b_sorted_intervals_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    results = load_results()
    intervals = load_intervals()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating Case 2B visualizations...")
    make_histogram_linear(intervals, results, OUTPUT_DIR)
    make_histogram_log(intervals, results, OUTPUT_DIR)
    make_qq_plot(intervals, results, OUTPUT_DIR)
    make_sorted_intervals(intervals, results, OUTPUT_DIR)

    print("All Case 2B visualizations complete.")


if __name__ == '__main__':
    main()
