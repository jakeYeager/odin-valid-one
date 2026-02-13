"""
Case 1: Visualization - Blind Study (Approach Two)
Generates 3 histograms (one per variable) with uniform baseline overlay,
plus a significance comparison plot.
All outputs saved to output/ directory.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_1_results_blind.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def make_histogram(var_name, var_results, output_dir):
    """Histogram with 16 bins and uniform expected-count baseline."""
    counts = var_results['bin_counts']
    expected = var_results['expected_count_per_bin']
    p_value = var_results['chi_square']['p_value']
    chi2 = var_results['chi_square']['statistic']

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [str(i) for i in range(1, 17)]
    colors = ['#c0392c' if c > expected else '#2980b9' for c in counts]
    ax.bar(labels, counts, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(y=expected, color='black', linestyle='--', linewidth=1.5,
               label=f'Expected (uniform): {expected:.1f}')
    ax.set_xlabel('Bin (1-16, equal width)')
    ax.set_ylabel('Observation Count')

    sig_label = "SIGNIFICANT" if p_value < 0.05 else "not significant"
    ax.set_title(f'{var_name} Distribution Uniformity Test\n'
                 f'Chi-square = {chi2:.2f}, p = {p_value:.4e} ({sig_label})')
    ax.legend()
    plt.tight_layout()

    path = os.path.join(output_dir, f'case_1_histogram_{var_name}_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_significance_comparison(results, output_dir):
    """Bar chart comparing chi-square p-values across variables."""
    variables = ['x_val', 'y_val', 'z_val']
    p_values = [results[v]['chi_square']['p_value'] for v in variables]

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ['#c0392c' if p < 0.05 else '#2ecc71' for p in p_values]
    bars = ax.bar(variables, p_values, color=colors, edgecolor='black', linewidth=0.5)

    ax.axhline(y=0.05, color='black', linestyle='--', linewidth=1.5,
               label='Significance threshold (p = 0.05)')
    ax.set_ylabel('Chi-square p-value')
    ax.set_title('Case 1: Distribution Uniformity — Significance Comparison')
    ax.legend()

    # Annotate bars with p-values
    for bar, p in zip(bars, p_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f'p = {p:.4e}', ha='center', va='bottom', fontsize=9)

    # Use log scale if values span wide range, otherwise linear
    max_p = max(p_values)
    if max_p > 0:
        ax.set_ylim(0, max(max_p * 1.3, 0.07))

    plt.tight_layout()

    path = os.path.join(output_dir, 'case_1_significance_comparison_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    results = load_results()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating Case 1 histograms...")
    for var in ['x_val', 'y_val', 'z_val']:
        make_histogram(var, results[var], OUTPUT_DIR)

    print("Generating significance comparison plot...")
    make_significance_comparison(results, OUTPUT_DIR)

    print("All Case 1 visualizations complete.")


if __name__ == '__main__':
    main()
