"""
Case 3A: Visualization - Blind Study (Approach Two)
Generates histograms (3), heatmaps (3), null hypothesis comparison plot,
and significance comparison plot for clustering pattern analysis.
All outputs saved to output/ directory.
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3a_results_blind.json')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def make_histogram(var_name, var_results, output_dir):
    """Histogram with 16 bins, colored by significance, with uniform baseline."""
    counts = var_results['bin_counts']
    expected = var_results['expected_count_per_bin']
    residuals = var_results['standardized_residuals']
    p_value = var_results['chi_square']['p_value']
    chi2 = var_results['chi_square']['statistic']
    cv = var_results['cramers_v']

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [str(i) for i in range(1, 17)]

    # Color: green=excess, red=deficit, blue=not significant (threshold=2.0)
    colors = []
    for r in residuals:
        if r > 2.0:
            colors.append('#27ae60')
        elif r < -2.0:
            colors.append('#c0392c')
        else:
            colors.append('#2980b9')

    ax.bar(labels, counts, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(y=expected, color='black', linestyle='--', linewidth=1.5,
               label=f'Expected (uniform): {expected:.1f}')

    ax.set_xlabel('Bin (1-16)')
    ax.set_ylabel('Record Count')

    sig_label = "SIGNIFICANT" if p_value < 0.05 else "not significant"
    ax.set_title(f'{var_name} Distribution (16 bins)\n'
                 f'χ² = {chi2:.2f}, p = {p_value:.4e} ({sig_label}), '
                 f"Cramér's V = {cv:.4f}")
    ax.legend()

    # Legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#27ae60', edgecolor='black', label='Significant excess'),
        Patch(facecolor='#c0392c', edgecolor='black', label='Significant deficit'),
        Patch(facecolor='#2980b9', edgecolor='black', label='Not significant'),
        plt.Line2D([0], [0], color='black', linestyle='--', label=f'Expected: {expected:.1f}')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.tight_layout()
    path = os.path.join(output_dir, f'case_3a_histogram_{var_name}_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_heatmap(var_name, df, var_results, output_dir):
    """Sequential heatmap: a_val groups on Y-axis, 16 bins on X-axis."""
    values = df[var_name].values
    a_vals = df['a_val'].values
    bin_size = var_results['bin_size']

    # Assign bins
    bin_indices = np.minimum(np.floor(values / bin_size).astype(int), 15)

    # Group by unique a_val values
    unique_a = np.sort(np.unique(a_vals))
    heatmap_data = np.zeros((len(unique_a), 16))

    for idx, a in enumerate(unique_a):
        mask = a_vals == a
        bins_for_a = bin_indices[mask]
        for b in bins_for_a:
            heatmap_data[idx, b] += 1

    fig, ax = plt.subplots(figsize=(12, max(6, len(unique_a) * 0.25)))
    im = ax.imshow(heatmap_data, aspect='auto', cmap='Reds', interpolation='nearest')

    ax.set_xticks(range(16))
    ax.set_xticklabels([str(i) for i in range(1, 17)])
    ax.set_xlabel('Bin (1-16)')

    # Show a_val labels (subsample if too many)
    if len(unique_a) > 40:
        step = max(1, len(unique_a) // 20)
        tick_positions = range(0, len(unique_a), step)
        ax.set_yticks(list(tick_positions))
        ax.set_yticklabels([str(int(unique_a[i])) for i in tick_positions])
    else:
        ax.set_yticks(range(len(unique_a)))
        ax.set_yticklabels([str(int(a)) for a in unique_a])

    ax.set_ylabel('a_val')
    ax.set_title(f'{var_name} Sequential Clustering')

    plt.colorbar(im, ax=ax, label='Record Count')
    plt.tight_layout()

    path = os.path.join(output_dir, f'case_3a_heatmap_{var_name}_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_null_hypothesis_comparison(results, output_dir):
    """Three subplots showing synthetic p-value distributions with real p-value overlay."""
    variables = ['x_val', 'y_val', 'z_val']
    synth = results['synthetic_null_hypothesis']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, var in zip(axes, variables):
        synthetic_p = synth[f'{var}_synthetic_p_values']
        real_p = results[var]['chi_square']['p_value']
        pct = synth['percentile_rank_analysis'][f'{var}_real_p_percentile']

        ax.hist(synthetic_p, bins=50, color='#95a5a6', edgecolor='black',
                linewidth=0.3, alpha=0.8, label='Synthetic p-values')
        ax.axvline(x=real_p, color='#c0392c', linewidth=2, linestyle='-',
                   label=f'Real p = {real_p:.4e}\n({pct:.1f}th percentile)')

        # Mark 5th percentile
        p5 = np.percentile(synthetic_p, 5)
        ax.axvline(x=p5, color='#f39c12', linewidth=1.5, linestyle='--',
                   label=f'5th percentile = {p5:.4f}')

        ax.set_xlabel('p-value')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{var}')
        ax.legend(fontsize=7)

    fig.suptitle('Case 3A: Null Hypothesis Comparison — Real vs. Synthetic p-values',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_3a_null_hypothesis_comparison_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_significance_comparison(results, output_dir):
    """Bar chart of p-values (log scale) with significance thresholds."""
    variables = ['x_val', 'y_val', 'z_val']
    synth = results['synthetic_null_hypothesis']

    p_values = [results[v]['chi_square']['p_value'] for v in variables]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Replace zero p-values with a small floor for log scale
    p_plot = [max(p, 1e-300) for p in p_values]
    colors = ['#c0392c' if p < 0.05 else '#2ecc71' for p in p_values]
    bars = ax.bar(variables, p_plot, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_yscale('log')
    ax.axhline(y=0.05, color='black', linestyle='--', linewidth=1.5,
               label='p = 0.05 threshold')

    # 5th and 95th percentiles of synthetic
    for var in variables:
        synth_p = synth[f'{var}_synthetic_p_values']
        p5 = np.percentile(synth_p, 5)
        p95 = np.percentile(synth_p, 95)

    # Use average synthetic percentiles for reference lines
    avg_p5 = np.mean([np.percentile(synth[f'{v}_synthetic_p_values'], 5) for v in variables])
    avg_p95 = np.mean([np.percentile(synth[f'{v}_synthetic_p_values'], 95) for v in variables])
    ax.axhline(y=avg_p5, color='#e67e22', linestyle=':', linewidth=1.2,
               label=f'Synthetic 5th pct ≈ {avg_p5:.4f}')
    ax.axhline(y=avg_p95, color='#3498db', linestyle=':', linewidth=1.2,
               label=f'Synthetic 95th pct ≈ {avg_p95:.4f}')

    # Annotate
    for bar, p in zip(bars, p_values):
        y_pos = max(p, 1e-300) * 2
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'p = {p:.2e}', ha='center', va='bottom', fontsize=9)

    ax.set_ylabel('Chi-square p-value (log scale)')
    ax.set_title('Case 3A: Clustering Significance Comparison')
    ax.legend(loc='upper left', fontsize=8)
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_3a_significance_comparison_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    results = load_results()
    df = load_data()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating Case 3A histograms...")
    for var in ['x_val', 'y_val', 'z_val']:
        make_histogram(var, results[var], OUTPUT_DIR)

    print("Generating Case 3A heatmaps...")
    for var in ['x_val', 'y_val', 'z_val']:
        make_heatmap(var, df, results[var], OUTPUT_DIR)

    print("Generating null hypothesis comparison plot...")
    make_null_hypothesis_comparison(results, OUTPUT_DIR)

    print("Generating significance comparison plot...")
    make_significance_comparison(results, OUTPUT_DIR)

    print("All Case 3A visualizations complete.")


if __name__ == '__main__':
    main()
