"""
Case 4A: Visualization - Energy-Weighted Clustering (Blind Study - Approach Two)
Generates energy histograms (3), count-vs-energy comparison, heatmaps (3),
null hypothesis comparison plot, and significance comparison plot.
All outputs saved to output/ directory.
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4a_results_blind.json')
CASE_3A_RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3a_results_blind.json')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def load_case_3a_results(path=CASE_3A_RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def make_energy_histogram(var_name, var_results, output_dir):
    """Energy histogram with 16 bins, colored by significance, with uniform baseline."""
    energy_per_bin = var_results['energy_per_bin']
    expected = var_results['expected_energy_per_bin']
    residuals = var_results['standardized_residuals']
    p_value = var_results['chi_square_energy']['p_value']
    chi2 = var_results['chi_square_energy']['statistic']
    cv = var_results['cramers_v']

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [str(i) for i in range(1, 17)]

    colors = []
    for r in residuals:
        if r > 2.0:
            colors.append('#27ae60')
        elif r < -2.0:
            colors.append('#c0392c')
        else:
            colors.append('#2980b9')

    ax.bar(labels, energy_per_bin, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(y=expected, color='black', linestyle='--', linewidth=1.5,
               label=f'Expected (uniform): {expected:.2e}')

    ax.set_xlabel('Bin (1-16)')
    ax.set_ylabel('Energy Sum')

    sig_label = "SIGNIFICANT" if p_value < 0.05 else "not significant"
    ax.set_title(f'{var_name} Energy Distribution (16 bins)\n'
                 f'χ² = {chi2:.2f}, p = {p_value:.4e} ({sig_label}), '
                 f"Cramér's V = {cv:.4f}")

    legend_elements = [
        Patch(facecolor='#27ae60', edgecolor='black', label='Significant excess'),
        Patch(facecolor='#c0392c', edgecolor='black', label='Significant deficit'),
        Patch(facecolor='#2980b9', edgecolor='black', label='Not significant'),
        plt.Line2D([0], [0], color='black', linestyle='--', label=f'Expected: {expected:.2e}')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

    plt.tight_layout()
    path = os.path.join(output_dir, f'case_4a_histogram_energy_{var_name}_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_count_vs_energy_comparison(results_4a, results_3a, output_dir):
    """Side-by-side comparison of count-based (3A) and energy-based (4A) histograms."""
    variables = ['x_val', 'y_val', 'z_val']

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    labels = [str(i) for i in range(1, 17)]

    for row, var in enumerate(variables):
        # Left: Case 3A count-based
        ax_count = axes[row, 0]
        counts = results_3a[var]['bin_counts']
        expected_count = results_3a[var]['expected_count_per_bin']
        res_3a = results_3a[var]['standardized_residuals']

        colors_3a = []
        for r in res_3a:
            if r > 2.0:
                colors_3a.append('#27ae60')
            elif r < -2.0:
                colors_3a.append('#c0392c')
            else:
                colors_3a.append('#2980b9')

        ax_count.bar(labels, counts, color=colors_3a, edgecolor='black', linewidth=0.5)
        ax_count.axhline(y=expected_count, color='black', linestyle='--', linewidth=1.2)
        p_3a = results_3a[var]['chi_square']['p_value']
        ax_count.set_title(f'{var} — Count (Case 3A)\nχ²={results_3a[var]["chi_square"]["statistic"]:.2f}, '
                           f'p={p_3a:.2e}')
        ax_count.set_ylabel('Record Count')
        if row == 2:
            ax_count.set_xlabel('Bin (1-16)')

        # Right: Case 4A energy-based
        ax_energy = axes[row, 1]
        energy = results_4a[var]['energy_per_bin']
        expected_energy = results_4a[var]['expected_energy_per_bin']
        res_4a = results_4a[var]['standardized_residuals']

        colors_4a = []
        for r in res_4a:
            if r > 2.0:
                colors_4a.append('#27ae60')
            elif r < -2.0:
                colors_4a.append('#c0392c')
            else:
                colors_4a.append('#2980b9')

        ax_energy.bar(labels, energy, color=colors_4a, edgecolor='black', linewidth=0.5)
        ax_energy.axhline(y=expected_energy, color='black', linestyle='--', linewidth=1.2)
        p_4a = results_4a[var]['chi_square_energy']['p_value']
        ax_energy.set_title(f'{var} — Energy (Case 4A)\nχ²={results_4a[var]["chi_square_energy"]["statistic"]:.2f}, '
                            f'p={p_4a:.2e}')
        ax_energy.set_ylabel('Energy Sum')
        if row == 2:
            ax_energy.set_xlabel('Bin (1-16)')

    fig.suptitle('Case 4A: Count-Based vs Energy-Weighted Clustering Comparison',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_4a_comparison_count_vs_energy_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_energy_heatmap(var_name, df, var_results, output_dir):
    """Sequential heatmap: a_val groups on Y-axis, 16 bins on X-axis, color = energy sum."""
    values = df[var_name].values
    a_vals = df['a_val'].values
    v_vals = df['v_val'].values
    energy = np.power(10, 1.5 * v_vals)
    bin_size = var_results['bin_size']

    bin_indices = np.minimum(np.floor(values / bin_size).astype(int), 15)

    unique_a = np.sort(np.unique(a_vals))
    heatmap_data = np.zeros((len(unique_a), 16))

    for idx, a in enumerate(unique_a):
        mask = a_vals == a
        bins_for_a = bin_indices[mask]
        energy_for_a = energy[mask]
        for b, e in zip(bins_for_a, energy_for_a):
            heatmap_data[idx, b] += e

    fig, ax = plt.subplots(figsize=(12, max(6, len(unique_a) * 0.25)))
    im = ax.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', interpolation='nearest')

    ax.set_xticks(range(16))
    ax.set_xticklabels([str(i) for i in range(1, 17)])
    ax.set_xlabel('Bin (1-16)')

    if len(unique_a) > 40:
        step = max(1, len(unique_a) // 20)
        tick_positions = range(0, len(unique_a), step)
        ax.set_yticks(list(tick_positions))
        ax.set_yticklabels([str(int(unique_a[i])) for i in tick_positions])
    else:
        ax.set_yticks(range(len(unique_a)))
        ax.set_yticklabels([str(int(a)) for a in unique_a])

    ax.set_ylabel('a_val')
    ax.set_title(f'{var_name} Energy Clustering - Sequential')

    plt.colorbar(im, ax=ax, label='Energy Sum')
    plt.tight_layout()

    path = os.path.join(output_dir, f'case_4a_heatmap_energy_{var_name}_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_null_hypothesis_comparison(results, output_dir):
    """Three subplots showing synthetic p-value distributions (energy-weighted)
    with real p-value overlay."""
    variables = ['x_val', 'y_val', 'z_val']
    synth = results['synthetic_null_hypothesis']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, var in zip(axes, variables):
        synthetic_p = synth[f'{var}_synthetic_p_values']
        real_p = results[var]['chi_square_energy']['p_value']
        pct = synth['percentile_rank_analysis'][f'{var}_real_p_percentile']

        ax.hist(synthetic_p, bins=50, color='#95a5a6', edgecolor='black',
                linewidth=0.3, alpha=0.8, label='Synthetic p-values')
        ax.axvline(x=real_p, color='#c0392c', linewidth=2, linestyle='-',
                   label=f'Real p = {real_p:.4e}\n({pct:.1f}th percentile)')

        p5 = np.percentile(synthetic_p, 5)
        ax.axvline(x=p5, color='#f39c12', linewidth=1.5, linestyle='--',
                   label=f'5th percentile = {p5:.4f}')

        ax.set_xlabel('p-value')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{var}')
        ax.legend(fontsize=7)

    fig.suptitle('Case 4A: Null Hypothesis Comparison — Energy-Weighted Real vs. Synthetic p-values',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_4a_null_hypothesis_comparison_energy_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_significance_comparison(results_4a, results_3a, output_dir):
    """Significance comparison: Case 3A (count) vs Case 4A (energy) on same plot."""
    variables = ['x_val', 'y_val', 'z_val']
    synth = results_4a['synthetic_null_hypothesis']

    p_3a = [results_3a[v]['chi_square']['p_value'] for v in variables]
    p_4a = [results_4a[v]['chi_square_energy']['p_value'] for v in variables]

    fig, ax = plt.subplots(figsize=(10, 7))
    x = np.arange(len(variables))
    width = 0.35

    # Floor zeros for log scale
    p_3a_plot = [max(p, 1e-300) for p in p_3a]
    p_4a_plot = [max(p, 1e-300) for p in p_4a]

    bars_3a = ax.bar(x - width / 2, p_3a_plot, width, color='#3498db',
                     edgecolor='black', linewidth=0.5, label='Case 3A (Count)')
    bars_4a = ax.bar(x + width / 2, p_4a_plot, width, color='#e74c3c',
                     edgecolor='black', linewidth=0.5, label='Case 4A (Energy)')

    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(variables)

    ax.axhline(y=0.05, color='black', linestyle='--', linewidth=1.5,
               label='p = 0.05 threshold')

    # Synthetic percentiles
    avg_p5 = np.mean([np.percentile(synth[f'{v}_synthetic_p_values'], 5) for v in variables])
    avg_p95 = np.mean([np.percentile(synth[f'{v}_synthetic_p_values'], 95) for v in variables])
    ax.axhline(y=avg_p5, color='#e67e22', linestyle=':', linewidth=1.2,
               label=f'Synthetic 5th pct ~ {avg_p5:.4f}')
    ax.axhline(y=avg_p95, color='#2ecc71', linestyle=':', linewidth=1.2,
               label=f'Synthetic 95th pct ~ {avg_p95:.4f}')

    # Annotate p-values
    for bar, p in zip(bars_3a, p_3a):
        y_pos = max(p, 1e-300) * 2
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'{p:.2e}', ha='center', va='bottom', fontsize=7, color='#2c3e50')
    for bar, p in zip(bars_4a, p_4a):
        y_pos = max(p, 1e-300) * 2
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f'{p:.2e}', ha='center', va='bottom', fontsize=7, color='#c0392b')

    ax.set_ylabel('Chi-square p-value (log scale)')
    ax.set_title('Case 4A: Significance Comparison — Count (3A) vs Energy (4A)')
    ax.legend(loc='upper left', fontsize=8)
    plt.tight_layout()

    path = os.path.join(output_dir, 'case_4a_significance_comparison_energy_blind.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    results_4a = load_results()
    results_3a = load_case_3a_results()
    df = load_data()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating Case 4A energy histograms...")
    for var in ['x_val', 'y_val', 'z_val']:
        make_energy_histogram(var, results_4a[var], OUTPUT_DIR)

    print("Generating count vs energy comparison...")
    make_count_vs_energy_comparison(results_4a, results_3a, OUTPUT_DIR)

    print("Generating Case 4A energy heatmaps...")
    for var in ['x_val', 'y_val', 'z_val']:
        make_energy_heatmap(var, df, results_4a[var], OUTPUT_DIR)

    print("Generating null hypothesis comparison plot (energy-weighted)...")
    make_null_hypothesis_comparison(results_4a, OUTPUT_DIR)

    print("Generating significance comparison plot...")
    make_significance_comparison(results_4a, results_3a, OUTPUT_DIR)

    print("All Case 4A visualizations complete.")


if __name__ == '__main__':
    main()
