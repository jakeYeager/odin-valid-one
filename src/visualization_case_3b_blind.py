"""
Case 3B: Visualization - Stratified Clustering Patterns (Blind Study - Approach Two)
Generates:
  - 3x4 histogram grid (variables × strata)
  - Effect size comparison across strata
  - Significance comparison across strata
  - Sequential heatmaps per stratum and variable (12 total)
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

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3b_results_blind.json')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')

VARIABLES = ['x_val', 'y_val', 'z_val']
STRATUM_NUMS = ['stratum_1', 'stratum_2', 'stratum_3', 'stratum_4']
STRATUM_LABELS = ['Q1 (0-25%)', 'Q2 (25-50%)', 'Q3 (50-75%)', 'Q4 (75-100%)']


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def create_strata(df, results):
    """Recreate strata from quartile boundaries in results."""
    q = results['v_val_quartiles']
    conditions = [
        df['v_val'] <= q[0],
        (df['v_val'] > q[0]) & (df['v_val'] <= q[1]),
        (df['v_val'] > q[1]) & (df['v_val'] <= q[2]),
        df['v_val'] > q[2],
    ]
    strata = {}
    for s_num, cond in zip(STRATUM_NUMS, conditions):
        strata[s_num] = df[cond].copy()
    return strata


def make_histogram_grid(results, output_dir):
    """3 rows (variables) × 4 columns (strata) histogram grid."""
    fig, axes = plt.subplots(3, 4, figsize=(20, 12))
    bin_labels = [str(i) for i in range(1, 17)]

    for row, var in enumerate(VARIABLES):
        for col, (s_num, s_label) in enumerate(zip(STRATUM_NUMS, STRATUM_LABELS)):
            ax = axes[row, col]
            vr = results[s_num][var]
            counts = vr['bin_counts']
            expected = vr['expected_count_per_bin']
            residuals = vr['standardized_residuals']
            p_value = vr['p_value']
            cv = vr['cramers_v']

            colors = []
            for r in residuals:
                if r > 2.0:
                    colors.append('#27ae60')
                elif r < -2.0:
                    colors.append('#c0392c')
                else:
                    colors.append('#2980b9')

            ax.bar(bin_labels, counts, color=colors, edgecolor='black', linewidth=0.3)
            ax.axhline(y=expected, color='black', linestyle='--', linewidth=1,
                       label=f'Expected: {expected:.1f}')

            if row == 2:
                ax.set_xlabel('Bin')
            if col == 0:
                ax.set_ylabel(f'{var}\nCount')

            sig = "SIG" if p_value < 0.05 else "ns"
            ax.set_title(f'{s_label}\np={p_value:.2e} ({sig}), V={cv:.4f}',
                         fontsize=8)
            ax.tick_params(labelsize=6)

    # Add shared legend
    legend_elements = [
        Patch(facecolor='#27ae60', edgecolor='black', label='Excess'),
        Patch(facecolor='#c0392c', edgecolor='black', label='Deficit'),
        Patch(facecolor='#2980b9', edgecolor='black', label='Not significant'),
        plt.Line2D([0], [0], color='black', linestyle='--', label='Expected (uniform)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Case 3B: Stratified Clustering — Histograms by Variable and v_val Quartile',
                 fontsize=14, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])

    path = os.path.join(output_dir, 'case_3b_histogram_grid_blind.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def make_effect_size_comparison(results, output_dir):
    """Three subplots showing Cramér's V across strata for each variable."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    x_pos = range(4)

    for ax, var in zip(axes, VARIABLES):
        cramers = [results[s_num][var]['cramers_v'] for s_num in STRATUM_NUMS]
        colors = ['#c0392c' if results[s_num][var]['p_value'] < 0.05 else '#2ecc71'
                  for s_num in STRATUM_NUMS]
        bars = ax.bar(x_pos, cramers, color=colors, edgecolor='black', linewidth=0.5)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
        ax.set_ylabel("Cramér's V")
        ax.set_title(f'{var}')
        ax.set_ylim(0, max(max(cramers) * 1.3, 0.05))

        for bar, v in zip(bars, cramers):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.001,
                    f'{v:.4f}', ha='center', va='bottom', fontsize=8)

    legend_elements = [
        Patch(facecolor='#c0392c', edgecolor='black', label='p < 0.05 (significant)'),
        Patch(facecolor='#2ecc71', edgecolor='black', label='p ≥ 0.05 (not significant)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("Case 3B: Cramér's V Effect Size by Stratum",
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])

    path = os.path.join(output_dir, 'case_3b_effect_size_comparison_blind.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def make_significance_comparison(results, output_dir):
    """Three subplots showing p-values (log scale) across strata with synthetic percentiles."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    x_pos = range(4)

    for ax, var in zip(axes, VARIABLES):
        p_values = [results[s_num][var]['p_value'] for s_num in STRATUM_NUMS]
        p_plot = [max(p, 1e-300) for p in p_values]
        colors = ['#c0392c' if p < 0.05 else '#2ecc71' for p in p_values]

        ax.bar(x_pos, p_plot, color=colors, edgecolor='black', linewidth=0.5)
        ax.set_yscale('log')
        ax.axhline(y=0.05, color='black', linestyle='--', linewidth=1.5,
                   label='p = 0.05')

        # Overlay 10th/90th percentiles from synthetic distributions
        for i, s_num in enumerate(STRATUM_NUMS):
            synth_p = results[s_num][var].get('synthetic_p_values', [])
            if synth_p:
                p10 = np.percentile(synth_p, 10)
                p90 = np.percentile(synth_p, 90)
                ax.plot(i, p10, marker='v', color='#e67e22', markersize=8, zorder=5)
                ax.plot(i, p90, marker='^', color='#3498db', markersize=8, zorder=5)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])
        ax.set_ylabel('p-value (log scale)')
        ax.set_title(f'{var}')

        for i, p in enumerate(p_values):
            ax.text(i, max(p, 1e-300) * 2, f'{p:.1e}', ha='center', va='bottom', fontsize=7)

    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#c0392c', edgecolor='black', label='p < 0.05'),
        Patch(facecolor='#2ecc71', edgecolor='black', label='p ≥ 0.05'),
        plt.Line2D([0], [0], color='black', linestyle='--', label='p = 0.05'),
        Line2D([0], [0], marker='v', color='#e67e22', linestyle='None', label='Synth 10th pct'),
        Line2D([0], [0], marker='^', color='#3498db', linestyle='None', label='Synth 90th pct'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, fontsize=8,
               bbox_to_anchor=(0.5, -0.04))

    fig.suptitle('Case 3B: Significance by Stratum (Chi-square p-value)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0.06, 1, 0.94])

    path = os.path.join(output_dir, 'case_3b_significance_by_stratum_blind.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def make_heatmaps(results, strata, output_dir):
    """Sequential heatmaps: 12 total (4 strata × 3 variables)."""
    for s_num, s_label in zip(STRATUM_NUMS, STRATUM_LABELS):
        sdf = strata[s_num]
        a_vals = sdf['a_val'].values

        for var in VARIABLES:
            values = sdf[var].values
            bin_size = results[s_num][var]['bin_size']

            bin_indices = np.minimum(np.floor(values / bin_size).astype(int), 15)

            unique_a = np.sort(np.unique(a_vals))
            heatmap_data = np.zeros((len(unique_a), 16))

            for idx, a in enumerate(unique_a):
                mask = a_vals == a
                for b in bin_indices[mask]:
                    heatmap_data[idx, b] += 1

            fig, ax = plt.subplots(figsize=(12, max(4, len(unique_a) * 0.2)))
            im = ax.imshow(heatmap_data, aspect='auto', cmap='Reds', interpolation='nearest')

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
            p_val = results[s_num][var]['p_value']
            ax.set_title(f'{var} — {s_label} (n={results[s_num]["sample_size"]}, p={p_val:.2e})')

            plt.colorbar(im, ax=ax, label='Record Count')
            plt.tight_layout()

            s_idx = s_num.split('_')[1]
            path = os.path.join(output_dir,
                                f'case_3b_heatmap_stratum_{s_idx}_{var}_blind.png')
            fig.savefig(path, dpi=150)
            plt.close(fig)
            print(f"  Saved: {path}")


def main():
    results = load_results()
    df = load_data()
    strata = create_strata(df, results)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating Case 3B histogram grid...")
    make_histogram_grid(results, OUTPUT_DIR)

    print("Generating Case 3B effect size comparison...")
    make_effect_size_comparison(results, OUTPUT_DIR)

    print("Generating Case 3B significance comparison...")
    make_significance_comparison(results, OUTPUT_DIR)

    print("Generating Case 3B heatmaps...")
    make_heatmaps(results, strata, OUTPUT_DIR)

    print("All Case 3B visualizations complete.")


if __name__ == '__main__':
    main()
